# 3-way comparison histogram for suspicion index
compare_plot <- function(var,
                         top = NULL,
                         mid = NULL,
                         bot = NULL,
                         top_label = "Rejected    (n = 43)",
                         mid_label = "Total    (n = 499)",
                         bot_label = "Eligible   (n = 456)",
                         bins = 10,
                         display = "none",
                         stat = "median",
                         labels = "right")
{defaults <- c(top = "p_rejected", mid = "p_full", bot = "p_eligible")
for (nm in names(defaults)) {
  if (is.null(get(nm))) {
    if (!exists(defaults[[nm]], envir = globalenv()))
      stop("Default object '", defaults[[nm]],
           "' not found. Either create it or pass a data frame to `", nm, "`.")
    assign(nm, get(defaults[[nm]], envir = globalenv()))
  }
}
panel_labels <- c(top = top_label, mid = mid_label, bot = bot_label)
panels <- list(top = top, mid = mid, bot = bot)
panel_names <- c("top", "mid", "bot"
)
stat_fn <- if (stat == "mean") mean else median
stat_label <- if (stat == "mean") "Mean" else "Median"

combined <- bind_rows(
  lapply(panel_names, \(nm) panels[[nm]] |> mutate(panel = panel_labels[[nm]]))
) |>
  mutate(panel = factor(panel, levels = panel_labels))

x_range <- range(combined[[var]], na.rm = TRUE)
bin_breaks <- seq(x_range[1], x_range[2], length.out = bins + 1)

stats <- bind_rows(
  lapply(panel_names, \(nm) {
    panels[[nm]] |>
      summarise(
        center = stat_fn(.data[[var]], na.rm = TRUE),
        min_val = min(.data[[var]], na.rm = TRUE),
        max_val = max(.data[[var]], na.rm = TRUE),
        panel = nm
      )
  })
) |>
  mutate(
    panel = factor(panel_labels[panel], levels = panel_labels),
    label = case_when(
      display == "min" ~ paste0(stat_label, ": ", round(center, 2), "\nMin: ", round(min_val, 2)),
      display == "max" ~ paste0(stat_label, ": ", round(center, 2), "\nMax: ", round(max_val, 2)),
      .default = paste0(stat_label, ": ", round(center, 2))
    )
  )

fill_colors <- setNames(c("red3", "darkgoldenrod2", "chartreuse4"), panel_labels)

ggplot(combined, aes(x = .data[[var]], fill = panel)) +
  geom_histogram(breaks = bin_breaks, alpha = 0.7) +
  geom_vline(data = stats, aes(xintercept = center),
             linetype = "dashed", linewidth = 0.8) +
  geom_text(data = stats,
            aes(x = if (labels == "left") -Inf else Inf, y = Inf, label = label),
            vjust = 1.2, hjust = if (labels == "left") -0.05 else 1.05,
            size = 3.5, lineheight = 0.9) +
  stat_bin(breaks = bin_breaks, geom = "text",
           aes(label = after_stat(ifelse(count > 0, count, ""))),
           vjust = -0.3, size = 3) +
  facet_wrap(~panel, ncol = 1, scales = "free_y") +
  scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +
  scale_fill_manual(values = fill_colors) +
  labs(x = var, y = "Count") +
  guides(fill = "none")
}
#-----------------------------------------------------------------------------

# Custom 3-way split for suspicion index
split_panel <- function(data = panel) {
  p_full     <- data |> filter(!is.na(gps_diff)) |> 
    filter(!grepl("_dupe", flag, fixed = TRUE))
  p_eligible <- p_full |> filter(is.na(flag))
  p_rejected <- p_full |>
    filter(!response_id %in% p_eligible$response_id) |>
    filter(!grepl("_dupe", flag, fixed = TRUE))
    
  
  assign("p_full",     p_full,     envir = parent.frame())
  assign("p_eligible", p_eligible, envir = parent.frame())
  assign("p_rejected", p_rejected, envir = parent.frame())
}
#-----------------------------------------------------------------------------

# Proportion summary table for suspicion index
prop_table <- function(var, full = NULL, eligible = NULL, rejected = NULL) {
  defaults <- c(full = "p_full", eligible = "p_eligible", rejected = "p_rejected")
  for (nm in names(defaults)) {
    if (is.null(get(nm))) {
      if (!exists(defaults[[nm]], envir = globalenv()))
        stop("Default object '", defaults[[nm]],
             "' not found. Either create it or pass a data frame to `", nm, "`.")
      assign(nm, get(defaults[[nm]], envir = globalenv()))
    }
  }

  bind_rows(
    rejected |> mutate(group = paste0("Rejected n=", nrow(rejected))),
    full     |> mutate(group = paste0("Full n=",     nrow(full))),
    eligible |> mutate(group = paste0("Eligible n=", nrow(eligible)))
  ) |>
    summarise(
      n_true = sum(.data[[var]], na.rm = TRUE),
      prop   = mean(.data[[var]], na.rm = TRUE),
      .by = group
    )
}
#----------------------------------------------------------------------------

# Model data prep and recipe builder
# Requires tidyverse and tidymodels to be loaded, and configs_llmpanel.R to be
# sourced, before calling the functions.
# See scripts/eda/6_panel_recipes.qmd for the design rationale.

# Resolve an interactions argument ("none", "all", or a subset) to a character
# vector. `available` is the subset allowed for the current options.
resolve_interactions <- function(requested, choices, available = choices, arg) {
  if (identical(requested, "all")) return(available)
  if (identical(requested, "none") || length(requested) == 0) return(character(0))
  unknown <- setdiff(requested, choices)
  if (length(unknown) > 0) {
    stop("Unknown `", arg, "`: ", paste(unknown, collapse = ", "),
         ". Use \"none\", \"all\", or any of: ", paste(choices, collapse = ", "), ".")
  }
  requested
}

# Convert pivoted panel_long (with engineered demographic features) to
# model-ready data for rec_llmpanel()
prep_llmpanel_data <- function(data) {
  required <- c("message_rating", llmpanel_controls, llmpanel_dem_constant,
                unique(llmpanel_feature_specs$var))
  missing_cols <- setdiff(required, names(data))
  if (length(missing_cols) > 0) {
    stop("`data` is missing required columns: ", paste(missing_cols, collapse = ", "),
         ". Run the feature engineering in 6_panel_recipes.qmd before pivoting.")
  }

  rating_levels <- c("strongly_disagree", "disagree", "somewhat_disagree", "neutral",
                     "somewhat_agree", "agree", "strongly_agree")
  formality_levels <- c("strongly_prefer_formal", "moderately_prefer_formal",
                        "slightly_prefer_formal", "slightly_prefer_informal",
                        "moderately_prefer_informal", "strongly_prefer_informal")
  education_levels <- c("less_than_high_school_or_ged_degree", "high_school_or_ged",
                        "some_college", "2_year_degree", "4_year_degree", "advanced_degree")
  income_levels <- c("Less than $25,000", "$25,000 - $37,499", "$37,500 - $49,999",
                     "$50,000 - $74,999", "$75,000 - $99,999", "$100,000 - $149,999",
                     "$150,000 - $199,999", "$200,000 or more")

  # Short labels give readable dummy column names
  data |>
    mutate(
      message_rating = as.numeric(factor(message_rating, levels = rating_levels)),
      across(q1_legitimizing_1:q5_norms_1,
             \(x) factor(x, levels = rating_levels, ordered = TRUE)),
      q6_formality_1 = factor(q6_formality_1, levels = formality_levels, ordered = TRUE),
      dem_age_binned = factor(dem_age_binned,
        labels = c("under_30", "age_30s", "age_40s", "age_50s", "age_60_plus"),
        ordered = TRUE),
      dem_education = factor(dem_education, levels = education_levels, ordered = TRUE),
      dem_edu_collapsed = factor(dem_edu_collapsed,
        levels = c("High School or Less", "Some College", "2-Year Degree or Higher"),
        labels = c("hs_or_less", "some_college", "degree_2yr_plus")),
      dem_income = factor(dem_income, levels = income_levels,
        labels = c("under_25k", "from_25k", "from_37k", "from_50k",
                   "from_75k", "from_100k", "from_150k", "from_200k"),
        ordered = TRUE),
      across(c(context, style, tone, survey_version), factor))
}
#----------------------------------------------------------------------------

# Shared recipe start: outcome, ID, controls, constant demographics
#   dummy: "treatment" drops the reference level (penalized linear models),
#          "one_hot" keeps a column for every level, "none" leaves nominal
#          controls as factors (engines that split factors natively)
rec_llmpanel_base <- function(data, dem_adjustable,
                              dummy = c("treatment", "one_hot", "none")) {
  dummy <- match.arg(dummy)
  rec_formula <- reformulate(
    c("subid", llmpanel_controls, llmpanel_dem_constant, dem_adjustable),
    response = "message_rating")

  rec <- recipe(rec_formula, data = data) |>
    update_role(subid, new_role = "id") |>
    step_ordinalscore(matches("^q[1-6]_"))
  if (dummy != "none") {
    rec <- rec |> step_dummy(context, style, tone, survey_version,
                             one_hot = dummy == "one_hot")
  }
  rec
}
#----------------------------------------------------------------------------

# Build a recipe for an algorithm from feature options
#   data:      output of prep_llmpanel_data()
#   algorithm: "glmnet", "xgboost", or "ranger"; sets the defaults for any
#              argument left NULL (see llmpanel_algorithm_defaults) and the
#              preprocessing (see llmpanel_algorithm_prep):
#                glmnet:  treatment dummies, step_nzv() on interaction
#                         columns, step_normalize()
#                xgboost: one-hot dummies, no step_nzv() or step_normalize()
#                         (splits are unaffected by scaling)
#                ranger:  nominal features stay factors (no dummies), no
#                         step_nzv() or step_normalize(); explicit
#                         interactions are not supported. Use
#                         respect.unordered.factors = "order" in the model spec.
#   age:       "numeric", "nominal" (binned, dummy coded), or "ordinal" (binned, scored)
#   education: "ordinal" (6 levels, scored) or "nominal" (collapsed to 3, dummy coded)
#   income:    "nominal" or "ordinal" income bracket; "adjusted" to use
#              household-adjusted income in place of the bracket; or
#              "nominal+adjusted" / "ordinal+adjusted" to add adjusted
#              income alongside the bracket
#   dem_interactions:  "all" (every interaction available for the income
#                      option), "none", or any subset of llmpanel_dem_interactions
#   base_interactions: "all", "none", or any subset of llmpanel_base_interactions
rec_llmpanel <- function(data,
                         algorithm = llmpanel_algorithms,
                         age = NULL,
                         education = NULL,
                         income = NULL,
                         dem_interactions = NULL,
                         base_interactions = NULL) {
  algorithm <- match.arg(algorithm)
  defaults <- llmpanel_algorithm_defaults[[algorithm]]
  age <- match.arg(age %||% defaults$age, llmpanel_age_options)
  education <- match.arg(education %||% defaults$education, llmpanel_education_options)
  income <- match.arg(income %||% defaults$income, llmpanel_income_options)
  dem_interactions <- dem_interactions %||% defaults$dem_interactions
  base_interactions <- base_interactions %||% defaults$base_interactions

  # Income x Household Size is not used whenever adjusted income is in the
  # model (alone or alongside the bracket), since it already incorporates
  # household size
  uses_adjusted <- grepl("adjusted", income, fixed = TRUE)
  available_dem <- if (uses_adjusted) {
    setdiff(llmpanel_dem_interactions, "income_household")
  } else {
    llmpanel_dem_interactions
  }
  dem_interactions <- resolve_interactions(dem_interactions, llmpanel_dem_interactions,
                                           available_dem, "dem_interactions")
  if (!all(dem_interactions %in% available_dem)) {
    stop("\"income_household\" is not available with `income = \"", income,
         "\"` because adjusted income already incorporates household size.")
  }
  base_interactions <- resolve_interactions(base_interactions, llmpanel_base_interactions,
                                            arg = "base_interactions")

  prep_opts <- llmpanel_algorithm_prep[llmpanel_algorithm_prep$algorithm == algorithm, ]
  if (!prep_opts$interactions && length(dem_interactions) + length(base_interactions) > 0) {
    stop("Explicit interactions are not supported for `algorithm = \"", algorithm,
         "\"` because nominal features stay as factors. Trees model interactions ",
         "through splits; leave `dem_interactions` and `base_interactions` as \"none\".")
  }

  specs <- dplyr::bind_rows(
    llmpanel_feature_specs[llmpanel_feature_specs$feature == "age" &
                             llmpanel_feature_specs$option == age, ],
    llmpanel_feature_specs[llmpanel_feature_specs$feature == "education" &
                             llmpanel_feature_specs$option == education, ],
    llmpanel_feature_specs[llmpanel_feature_specs$feature == "income" &
                             llmpanel_feature_specs$option == income, ])
  vars_with <- \(enc) specs$var[specs$encoding %in% enc]

  rec <- rec_llmpanel_base(data, specs$var, dummy = prep_opts$dummy)
  # step_dummy() turns ordered factors into polynomial contrasts (linear,
  # quadratic, ...) rather than 0/1 indicators. Unordering first gives
  # treatment-coded indicators, so glmnet penalizes each level's deviation
  # from the reference rather than higher-order trend terms. Without dummies
  # (ranger), unordering lets the engine treat the levels as categories.
  if (length(vars_with("nominal_ordered")) > 0) {
    rec <- rec |> step_unorder(all_of(vars_with("nominal_ordered")))
  }
  if (length(vars_with("ordinal")) > 0) {
    rec <- rec |> step_ordinalscore(all_of(vars_with("ordinal")))
  }
  if (prep_opts$dummy != "none" && length(vars_with(c("nominal", "nominal_ordered"))) > 0) {
    rec <- rec |> step_dummy(all_of(vars_with(c("nominal", "nominal_ordered"))),
                             one_hot = prep_opts$dummy == "one_hot")
  }

  if (length(dem_interactions) > 0) {
    term_for <- \(feat) na.omit(specs$int_term[specs$feature == feat])
    age_term <- term_for("age")
    edu_term <- term_for("education")
    inc_term <- term_for("income")

    dem_formulas <- c(
      age_income_education = paste0("~ (", age_term, " + ", inc_term, " + ", edu_term, ")^3"),
      sex_race_orientation = "~ (dem_sex + dem_race + dem_orientation)^3",
      age_household = paste0("~ ", age_term, ":dem_n_household"),
      income_household = paste0("~ ", inc_term, ":dem_n_household"))
    # Fixed order keeps output columns consistent regardless of argument order
    for (f in dem_formulas[intersect(llmpanel_dem_interactions, dem_interactions)]) {
      rec <- rec |> step_interact(terms = !!as.formula(f))
    }
  }

  if (length(base_interactions) > 0) {
    base_formulas <- c(
      attitudes_tone = paste0('~ matches("^q[1-5]_(?!.*_x_)", perl = TRUE):',
                              'matches("^tone_(?!.*_x_)", perl = TRUE)'),
      formality_style = '~ q6_formality_1:matches("^style_(?!.*_x_)", perl = TRUE)')
    for (f in base_formulas[intersect(llmpanel_base_interactions, base_interactions)]) {
      rec <- rec |> step_interact(terms = !!as.formula(f))
    }
  }

  # Sparse interaction columns destabilize penalized fits; trees just rarely
  # split on them, so the filter is glmnet-only
  if (prep_opts$nzv && length(dem_interactions) + length(base_interactions) > 0) {
    rec <- rec |> step_nzv(contains("_x_"))
  }

  rec <- rec |> step_zv(all_predictors())
  if (prep_opts$normalize) {
    rec <- rec |> step_normalize(all_predictors())
  }
  rec
}
#----------------------------------------------------------------------------

# A helper function for reviewing feature sets

review_features <- function(feat) {
  predictors <- setdiff(names(feat), c("subid", "message_rating"))
  dem <- str_subset(predictors, "^dem_")
  tibble(
    n_obs = nrow(feat),
    n_predictors = length(predictors),
    n_dem_main = sum(!str_detect(dem, "_x_")),
    n_dem_interactions = sum(str_detect(dem, "_x_")),
    n_base_interactions = sum(str_detect(predictors, "^q[1-6]_.*_x_")),
    n_missing = sum(is.na(feat))
  ) |>
    print()
  feat |>
    select(all_of(dem), -contains("_x_")) |>
    glimpse()
}

# A helper for counting predictors after prep, used in the configuration tables below:
  
count_predictors <- \(r)
r |> prep() |> bake(new_data = NULL) |> select(-subid, -message_rating) |> ncol()

# Format the wide panel. With long = TRUE, return one row per message rating instead:
# the demographic and preference columns plus survey_version, context, style, tone,
# message_rating (text), and rating_num (1-7).
format_eda <- function (d, long = FALSE){
  
  likert_cols <- c(
    "pref_legitimizing",
    "pref_self_efficacy",
    "pref_acknowledging",
    "pref_value_affirmation",
    "pref_norms")
  
  d <- d |>
    # Rename vars
    rename( 
      pref_legitimizing = q1_legitimizing_1,
      pref_self_efficacy = q2_self_efficacy_1,
      pref_acknowledging = q3_acknowledging_1,
      pref_value_affirmation = q4_value_affirmation_1,
      pref_norms = q5_norms_1,
      pref_formality = q6_formality_1) |>
    
    # Numericize likert scales
    mutate(across(all_of(likert_cols),
                  ~ case_when(
                    .x == "strongly_disagree" ~ 1,
                    .x == "disagree"          ~ 2,
                    .x == "somewhat_disagree" ~ 3,
                    .x == "neutral"           ~ 4,
                    .x == "somewhat_agree"    ~ 5,
                    .x == "agree"             ~ 6,
                    .x == "strongly_agree"    ~ 7))) |>
    
    # Numericize formality scale
    mutate(
      pref_formality = case_when(
        pref_formality == "strongly_prefer_informal"   ~ 1,
        pref_formality == "moderately_prefer_informal" ~ 2,
        pref_formality == "slightly_prefer_informal"   ~ 3,
        pref_formality == "slightly_prefer_formal"     ~ 4,
        pref_formality == "moderately_prefer_formal"   ~ 5,
        pref_formality == "strongly_prefer_formal"     ~ 6),
      
      # Numericize income scale
      dem_income_num = case_when(
        dem_income == "Less than $25,000"   ~ 12500,   # Midpoint estimates for each bracket
        dem_income == "$25,000 - $37,499"   ~ 31250,
        dem_income == "$37,500 - $49,999"   ~ 43750,
        dem_income == "$50,000 - $74,999"   ~ 62500,
        dem_income == "$75,000 - $99,999"   ~ 87500,
        dem_income == "$100,000 - $149,999" ~ 125000,
        dem_income == "$150,000 - $199,999" ~ 175000,
        dem_income == "$200,000 or more"    ~ 250000), # The cap for this one is debatable
      
      # Household-adjust income
      dem_income_num = dem_income_num / sqrt(dem_n_household),
      
      # Collapse categories for orientation
      dem_orientation = if_else(
        dem_orientation == "straight", "straight", "other"),
      
      # Collapse categories for race
      race_white = !is.na(dem_race_white),
      race_other =
        !is.na(dem_race_native_alaskan) |
        !is.na(dem_race_asian) |
        !is.na(dem_race_hispanic) |
        !is.na(dem_race_black),
      dem_ethnicity = if_else(race_white & !race_other, "white_only", "other")) |> 
    
    # Drop columns not used for modelling
    select(subid, contains("pref_"), contains("dem_"),
           -contains("race"), -dem_marital_status,
           -dem_identity, -dem_n_household, -dem_student, contains("_hi_"),
           contains("_hd_"), contains("_li_"), -contains("timing"))

  if (!long) return(d)

  rating_levels <- c("strongly_disagree", "disagree", "somewhat_disagree", "neutral",
                     "somewhat_agree", "agree", "strongly_agree")

  # Pivot the 120 message-rating columns to one row per message rating
  d |>
    select(subid, starts_with("dem_"), all_of(c(likert_cols, "pref_formality")),
           matches("^x[0-9]+_(hi|hd|li)_[0-9]+_"),
           -contains("timing"), -contains("attention")) |>
    pivot_longer(
      cols = matches("^x[0-9]+_(hi|hd|li)_[0-9]+_"),
      values_to = "message_rating",
      names_to = "message_type") |>
    separate(message_type,
             sep = "_", into = c(
               "survey_version", "context", "q_num", "tone_style"),
             extra = "drop") |>
    mutate(
      style = if_else(substr(tone_style, 1, 1) == "f", "formal", "informal"),
      tone = case_when(
        substr(tone_style, 2, 2) == "l" ~ "legitimizing",
        substr(tone_style, 2, 2) == "n" ~ "norms",
        substr(tone_style, 2, 2) == "s" ~ "self_efficacy",
        substr(tone_style, 2, 2) == "a" ~ "acknowledging",
        substr(tone_style, 2, 2) == "v" ~ "value_affirmation"),
      context = case_when(
        context == "hi" ~ "high_increasing",
        context == "hd" ~ "high_decreasing",
        context == "li" ~ "low_increasing")) |>
    select(-q_num, -tone_style) |>
    filter(!is.na(message_rating),
           str_trim(message_rating) != "") |>
    mutate(rating_num = as.numeric(factor(message_rating, levels = rating_levels)))
}



# Change in mean message rating from a reference tone to every other tone,
# among respondents whose highest-rated tone (ties included) is the reference.
# `extremes` has subid and list column rating_top; `ratings` has subid, tone, rating.
# Respondents who rated all five tones identically are excluded.
plot_change_from_top <- function(ref_tone, extremes, ratings, colors) {
  ref_label <- str_replace(ref_tone, "_", " ")

  ids <- extremes |>
    filter(map_lgl(rating_top, \(x) ref_tone %in% x), lengths(rating_top) < 5) |>
    pull(subid)

  changes <- ratings |>
    filter(subid %in% ids, !is.na(rating)) |>
    mutate(change = rating - rating[tone == ref_tone], .by = subid) |>
    filter(tone != ref_tone) |>
    mutate(tone = fct_reorder(as.character(tone), change, mean))

  tests <- changes |>
    summarise(
      mean_change = mean(change),
      p = tryCatch(wilcox.test(change, mu = 0, exact = FALSE)$p.value,
                   error = \(e) NA_real_),
      .by = tone) |>
    mutate(p_adj = p.adjust(p, method = "holm"),
           label = if_else(p_adj < .001, "p < .001",
                           paste0("p = ", sub("^0", "", sprintf("%.3f", p_adj)))))

  plot <- changes |>
    ggplot(aes(x = tone, y = change, fill = tone)) +
    geom_hline(yintercept = 0, linetype = "dashed") +
    geom_boxplot(show.legend = FALSE) +
    geom_text(data = tests, aes(x = tone, y = Inf, label = label),
              vjust = 1.5, inherit.aes = FALSE) +
    stat_summary(fun = mean, geom = "point", shape = 23, size = 2, fill = "white") +
    stat_summary(fun = mean, geom = "text",
                 aes(label = round(after_stat(y), 2)), vjust = -1) +
    scale_fill_manual(values = colors) +
    scale_x_discrete(labels = \(x) str_to_sentence(str_replace(x, "_", " "))) +
    labs(x = "Tone", y = paste("Change in mean rating vs.", ref_label),
         subtitle = paste0("Respondents with ", ref_label, " rated highest (n = ",
                           length(ids), "); p-values: Wilcoxon signed-rank vs. 0, Holm-adjusted"))

  list(plot = plot, tests = tests, n = length(ids))
}

# Distribution of mean message ratings across all tones, among respondents whose
# highest-rated (end = "top") or lowest-rated (end = "bottom") tone on the preferences
# survey (ties included) is `top_tone`.
# `panel` has subid, the list columns pref_top and pref_bottom, and the logical
# pref_straightline; `ratings` has subid, tone, rating. Straightliners are excluded.
plot_ratings_by_pref_top <- function(top_tone, panel, ratings, colors,
                                     end = c("top", "bottom")) {
  end <- match.arg(end)
  top_label <- str_replace(top_tone, "_", " ")
  pref_col <- paste0("pref_", end)

  ids <- panel |>
    filter(map_lgl(.data[[pref_col]], \(x) top_tone %in% x), !pref_straightline) |>
    pull(subid)

  plot <- ratings |>
    filter(subid %in% ids, !is.na(rating)) |>
    mutate(tone = fct_reorder(as.character(tone), rating, mean)) |>
    ggplot(aes(x = tone, y = rating, fill = tone)) +
    geom_boxplot(show.legend = FALSE) +
    stat_summary(fun = mean, geom = "point", shape = 23, size = 2, fill = "white") +
    stat_summary(fun = mean, geom = "text",
                 aes(label = round(after_stat(y), 2)), vjust = -1) +
    scale_fill_manual(values = colors) +
    scale_x_discrete(labels = \(x) str_to_sentence(str_replace(x, "_", " "))) +
    scale_y_continuous(limits = c(1, 7), breaks = 1:7) +
    labs(x = "Tone", y = "Mean Message Rating",
         subtitle = paste0("Respondents with ", top_label,
                           " rated ", if_else(end == "top", "highest", "lowest"),
                           " on preferences (n = ", length(ids),
                           "; straightliners excluded)"))

  list(plot = plot, n = length(ids))
}

# Among respondents whose highest-preferred tone (ties included) is `top_tone`,
# plot each respondent's change in message rating from `top_tone` to every other
# tone. Changes are positive when a tone was rated higher than the preferred tone.
# Same inputs as plot_ratings_by_pref_top(); straightliners are excluded.
plot_change_from_pref_top <- function(top_tone, panel, ratings, colors) {
  top_label <- str_replace(top_tone, "_", " ")

  ids <- panel |>
    filter(map_lgl(pref_top, \(x) top_tone %in% x), !pref_straightline) |>
    pull(subid)

  changes <- ratings |>
    filter(subid %in% ids, !is.na(rating)) |>
    mutate(tone = as.character(tone),
           change = rating - rating[tone == top_tone], .by = subid) |>
    filter(tone != top_tone) |>
    mutate(tone = fct_reorder(tone, change, mean))

  tests <- changes |>
    summarise(
      mean_change = mean(change),
      p = tryCatch(wilcox.test(change, mu = 0, exact = FALSE)$p.value,
                   error = \(e) NA_real_),
      .by = tone) |>
    mutate(p_adj = p.adjust(p, method = "holm"),
           label = if_else(p_adj < .001, "p < .001",
                           paste0("p = ", sub("^0", "", sprintf("%.3f", p_adj)))))

  plot <- changes |>
    ggplot(aes(x = tone, y = change, fill = tone)) +
    geom_hline(yintercept = 0, linetype = "dashed") +
    geom_boxplot(show.legend = FALSE) +
    geom_text(data = tests, aes(x = tone, y = Inf, label = label),
              vjust = 1.5, inherit.aes = FALSE) +
    stat_summary(fun = mean, geom = "point", shape = 23, size = 2, fill = "white") +
    stat_summary(fun = mean, geom = "text",
                 aes(label = round(after_stat(y), 2)), vjust = -1) +
    scale_fill_manual(values = colors) +
    scale_x_discrete(labels = \(x) str_to_sentence(str_replace(x, "_", " "))) +
    labs(x = "Tone", y = paste("Change in mean rating vs.", top_label),
         subtitle = paste0("Respondents with ", top_label, " preferred (n = ", length(ids),
                           "; straightliners excluded); p-values: Wilcoxon signed-rank vs. 0, Holm-adjusted"))

  list(plot = plot, tests = tests, n = length(ids))
}

# Compare a logical grouping column against a set of columns: Welch t-test and
# Cohen's d for numeric columns, chi-square (Fisher's exact when any expected
# count is below 5) and Cramer's V for the rest. p-values are also adjusted
# across all columns with Benjamini-Hochberg.
compare_groups <- function(data, group, cols) {
  group <- rlang::as_name(rlang::ensym(group))

  map(cols, \(v) {
    d <- data |>
      select(g = all_of(group), x = all_of(v)) |>
      drop_na()
    if (n_distinct(d$x) < 2 || n_distinct(d$g) < 2) return(NULL)

    if (is.numeric(d$x)) {
      x1 <- d$x[d$g]
      x0 <- d$x[!d$g]
      pooled_sd <- sqrt(((length(x1) - 1) * var(x1) + (length(x0) - 1) * var(x0)) /
                          (length(x1) + length(x0) - 2))
      tibble(variable = v, type = "numeric", n = nrow(d), test = "Welch t-test",
             group = sprintf("%.2f", mean(x1)), rest = sprintf("%.2f", mean(x0)),
             effect = (mean(x1) - mean(x0)) / pooled_sd,
             p = t.test(x1, x0)$p.value)
    } else {
      tab <- table(d$x, d$g)
      chi <- suppressWarnings(chisq.test(tab, correct = FALSE))
      small <- any(chi$expected < 5)
      tibble(variable = v, type = "categorical", n = nrow(d),
             test = if (small) "Fisher's exact" else "Chi-square",
             group = "", rest = "",
             effect = sqrt(unname(chi$statistic) / (sum(tab) * (min(dim(tab)) - 1))),
             p = if (small) {
               tryCatch(fisher.test(tab)$p.value,
                        error = \(e) fisher.test(tab, simulate.p.value = TRUE, B = 1e4)$p.value)
             } else chi$p.value)
    }
  }) |>
    list_rbind() |>
    mutate(p_adj = p.adjust(p, method = "BH")) |>
    arrange(p)
}

# ---------------------------------------------------------------------------
# Tone assignment methods (used by scripts/tone_assignment_methods.qmd)
# Requires tidyverse to be loaded. `tone_means` is a data frame of each
# respondent's mean rating per tone (subid, tone, rating).
# ---------------------------------------------------------------------------

# Histogram of respondent-level mean ratings with the mean and SD marked
plot_rating_hist <- function(data, col, title, fill = "steelblue") {
  x <- data[[col]]
  m <- mean(x, na.rm = TRUE)
  s <- sd(x, na.rm = TRUE)

  ggplot(data, aes(x = .data[[col]])) +
    annotate("rect", xmin = m - s, xmax = m + s, ymin = -Inf, ymax = Inf,
             fill = "firebrick", alpha = 0.12) +
    geom_histogram(binwidth = 0.25, boundary = 1, fill = fill, color = "white") +
    geom_vline(xintercept = m, color = "firebrick", linewidth = 0.8) +
    annotate("text", x = 0.8, y = Inf, hjust = 0, vjust = 1.5,
             label = paste0("Mean = ", round(m, 2), "\nSD = ", round(s, 2))) +
    scale_x_continuous(breaks = 1:7) +
    scale_y_continuous(expand = expansion(mult = c(0, 0.1))) +
    coord_cartesian(xlim = c(0.75, 7.25)) +
    labs(x = "Mean message rating", y = "Respondents", title = title,
         subtitle = paste0("n = ", sum(!is.na(x)), "; shaded band = mean ± 1 SD"))
}

# Each respondent's highest- (fn = max) or lowest-rated (fn = min) tone(s) and their
# rating, with every tied tone in its own column: <tone_prefix>_1 ... <tone_prefix>_<n_max>
# (NA where a respondent has fewer tied tones). Stops if any tie is larger than n_max.
extreme_tones_wide <- function(ratings, fn, rating_name, tone_prefix, n_max = 4) {
  tied <- ratings |>
    filter(near(rating, fn(rating)), .by = subid) |>
    mutate(k = row_number(), .by = subid)
  if (max(tied$k) > n_max) {
    stop("A respondent has more than ", n_max, " tied tones; increase `n_max`.")
  }

  rating_tbl <- tied |> summarise(rating = first(rating), .by = subid)
  names(rating_tbl)[2] <- rating_name

  tone_tbl <- tied |>
    select(subid, k, tone) |>
    complete(subid, k = seq_len(n_max)) |>
    pivot_wider(names_from = k, values_from = tone, names_prefix = paste0(tone_prefix, "_"))

  left_join(rating_tbl, tone_tbl, by = "subid")
}

# Long format (subid, tone) of the tied tones stored in <tone_prefix>_* columns
tied_tones_long <- function(data, tone_prefix) {
  data |>
    select(subid, starts_with(paste0(tone_prefix, "_"))) |>
    pivot_longer(-subid, values_to = "tone") |>
    drop_na(tone) |>
    select(subid, tone)
}

# Add a row for one method to a tracking tibble (replacing any row with the same name).
#   tracker: existing tracking tibble (NULL to start a new one)
#   method:  data frame with subid and one rating column (as for compare_methods())
#   kept:    tones the method uses. A character vector (same tones for every respondent)
#            or a data frame with subid and tone (tones used per respondent).
#            Kept tones are shown in equal proportion unless `weights` is given.
#   weights: optional how often each tone is shown (rescaled to sum to 1 per respondent;
#            tones with weight 0 are not used). Use instead of `kept`. Either a named numeric
#            vector (same weights for every respondent) or a data frame with subid, tone,
#            and weight (weights per respondent, e.g. from preference_weights()).
#   name:    row label (default: the data frame's "label" attribute)
#   tone_ratings: data frame with subid, tone, rating (each respondent's mean
#            rating per tone). Defaults to `tone_means`, as built in the calling script.
# Reported columns:
#   mean, sd:       respondent-level mean helpfulness and its SD
#   weighted_opt:   average share of a respondent's messages written in their
#                   highest-rated tone(s) (all tied tones count)
#   weighted_dis:   average share of a respondent's messages written in their
#                   lowest-rated tone(s) (all tied tones count)
track_method <- function(tracker, method, kept = NULL, name = NULL, weights = NULL,
                         tone_ratings = tone_means) {
  name <- name %||% attr(method, "label") %||% deparse(substitute(method))
  col <- setdiff(names(method)[map_lgl(method, is.numeric)], "subid")
  if (length(col) != 1) stop("`method` must have exactly one numeric rating column besides `subid`.")
  if (is.null(kept) && is.null(weights)) stop("Supply `kept` or `weights`.")

  # How often each respondent sees each kept tone
  exposure_long <- if (is.data.frame(weights)) {
    weights |>
      filter(subid %in% method$subid, weight > 0) |>
      select(subid, tone, weight)
  } else if (!is.null(weights)) {
    expand_grid(subid = method$subid,
                tibble(tone = names(weights), weight = unname(weights))) |>
      filter(weight > 0)
  } else {
    kept_long <- if (is.data.frame(kept)) kept else expand_grid(subid = method$subid, tone = kept)
    mutate(kept_long, weight = 1)
  }
  exposure <- exposure_long |>
    mutate(weight = weight / sum(weight), .by = subid) |>
    summarise(kept = list(tone), weight = list(weight), .by = subid)

  respondents <- tone_ratings |>
    summarise(top = list(tone[near(rating, max(rating))]),
              bottom = list(tone[near(rating, min(rating))]),
              .by = subid) |>
    inner_join(exposure, by = "subid") |>
    filter(subid %in% method$subid) |>
    mutate(weighted_opt = pmap_dbl(list(top, kept, weight), \(t, k, w) sum(w[k %in% t])),
           weighted_dis = pmap_dbl(list(bottom, kept, weight), \(b, k, w) sum(w[k %in% b])))

  ratings <- method[[col]]
  row <- tibble(
    method = name,
    mean = mean(ratings),
    sd = sd(ratings),
    weighted_opt = mean(respondents$weighted_opt),
    weighted_dis = mean(respondents$weighted_dis))

  if (is.null(tracker)) return(row)
  bind_rows(filter(tracker, method != name), row)
}

# Stack the distributions of up to 3 methods vertically on the same scale.
#   top, mid, bot: data frames with subid and one rating column, in stacking order.
#                  Leave any blank and the remaining two are stacked, e.g.
#                  compare_methods(top = panel_worst, bot = panel_best)
#                  compare_methods(top = panel_uniform, mid = panel_2tone, bot = panel_best)
# Each data frame's "label" and "fill" attributes set its facet label and color;
# otherwise the label comes from the object name ("panel_mean" -> "Mean") and the
# fill is steelblue. The subtitle gives each panel's mean paired difference from
# the bottom panel.
compare_methods <- function(top = NULL, mid = NULL, bot = NULL) {
  nm <- c(top = deparse(substitute(top)),
          mid = deparse(substitute(mid)),
          bot = deparse(substitute(bot)))
  panels <- compact(list(top = top, mid = mid, bot = bot))
  if (length(panels) < 2) stop("Supply at least two of `top`, `mid`, and `bot`.")

  info <- imap(panels, \(df, pos) {
    col <- setdiff(names(df)[map_lgl(df, is.numeric)], "subid")
    if (length(col) != 1) {
      stop("`", pos, "` must have exactly one numeric rating column besides `subid`.")
    }
    list(
      data = df |> transmute(subid, rating = .data[[col]]),
      label = attr(df, "label") %||%
        (nm[[pos]] |> str_remove("^panel_") |> str_replace_all("_", " ") |> str_to_sentence()),
      fill = attr(df, "fill") %||% "steelblue")
  })

  labels <- map_chr(info, "label")
  if (anyDuplicated(labels)) stop("Each stacked method needs a distinct label.")
  fills <- setNames(map_chr(info, "fill"), labels)

  cases <- imap(info, \(x, pos) mutate(x$data, case = x$label)) |>
    list_rbind() |>
    mutate(case = factor(case, levels = labels))

  stats <- cases |>
    summarise(mean = mean(rating), sd = sd(rating), .by = case) |>
    mutate(label = paste0("Mean = ", round(mean, 2), "
SD = ", round(sd, 2)))

  ref <- info[[length(info)]]
  gaps <- info[-length(info)] |>
    map_dbl(\(x) {
      j <- inner_join(x$data, ref$data, by = "subid", suffix = c(".x", ".ref"))
      mean(j$rating.x - j$rating.ref)
    })
  gap_text <- paste0(labels[-length(labels)], " ", sprintf("%+.2f", gaps), collapse = "; ")

  cases |>
    ggplot(aes(x = rating, fill = case)) +
    geom_rect(data = stats, inherit.aes = FALSE,
              aes(xmin = mean - sd, xmax = mean + sd, ymin = -Inf, ymax = Inf),
              fill = "firebrick", alpha = 0.12) +
    geom_histogram(binwidth = 0.25, boundary = 1, color = "white", show.legend = FALSE) +
    geom_vline(data = stats, aes(xintercept = mean),
               color = "firebrick", linewidth = 0.8) +
    geom_text(data = stats, inherit.aes = FALSE,
              aes(label = label), x = 0.8, y = Inf, hjust = 0, vjust = 1.3) +
    facet_grid(rows = vars(case)) +
    scale_fill_manual(values = fills) +
    scale_x_continuous(breaks = 1:7) +
    scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +
    coord_cartesian(xlim = c(0.75, 7.25)) +
    labs(x = "Mean message rating", y = "Respondents",
         title = "Mean message rating by assignment method",
         subtitle = paste0("Mean difference vs. ", ref$label, ": ", gap_text,
                           "; shaded band = mean ± 1 SD"))
}

# Tones kept for each respondent after dropping their least-preferred tones.
#   prefs:  data frame with subid, tone, and pref (preference score for that tone)
#   n_drop: how many of the lowest-preferred tones to drop. Tones tied at the cutoff
#           are dropped together, so a tie can drop more than n_drop tones. If that
#           would drop every tone (all tones tied), none are dropped.
# Returns a data frame with subid and tone for the kept tones.
drop_least_preferred <- function(prefs, n_drop) {
  prefs |>
    drop_na(pref) |>
    mutate(cutoff = sort(pref)[min(n_drop, n())],
           drop = pref <= cutoff,
           keep = !drop | all(drop),
           .by = subid) |>
    filter(keep) |>
    select(subid, tone)
}

# Per-respondent tone weights from preference scores, for weighting a respondent's
# tone ratings. A tone's weight is proportional to (preference score - offset)^power,
# so higher-preferred tones are shown more often (tied tones get equal weights).
# power = 1 weights in proportion to the score; larger powers sharpen the weighting
# toward the most-preferred tones. With offset = 1 a tone at the scale minimum is
# never shown, and a respondent whose weights would all be zero (every tone at the
# minimum) gets equal weights.
#   prefs:  data frame with subid, tone, and pref (preference score for that tone)
#   offset: value subtracted from each preference score before weighting
#   power:  exponent applied to (pref - offset); must be positive
# Returns a data frame with subid, tone, pref, and weight (weights sum to 1 per subid).
preference_weights <- function(prefs, offset = 1, power = 1) {
  stopifnot(power > 0)
  prefs |>
    drop_na(pref) |>
    mutate(raw = pmax(pref - offset, 0)^power,
           weight = if (sum(raw) > 0) raw / sum(raw) else 1 / n(),
           .by = subid) |>
    select(subid, tone, pref, weight)
}

# Per-respondent tone weights from preference tiers. Tones are sorted into tiers by
# preference score (tier 1 = highest score; tied tones share a tier), and each tone's
# weight is proportional to ratio^-(tier - 1), so with ratio = 2 tier 1 is shown twice
# as often as tier 2, four times as often as tier 3, and so on. Tied tones each get
# their tier's weight. Only the order of the preferences matters, not how far apart
# the scores are.
#   prefs: data frame with subid, tone, and pref (preference score for that tone)
#   ratio: how many times more often each tier is shown than the next tier down
# Returns a data frame with subid, tone, pref, tier, and weight (sums to 1 per subid).
tier_weights <- function(prefs, ratio = 2) {
  prefs |>
    drop_na(pref) |>
    mutate(tier = dense_rank(desc(pref)),
           raw = ratio^-(tier - 1),
           weight = raw / sum(raw),
           .by = subid) |>
    select(subid, tone, pref, tier, weight)
}

# Each respondent's weighted mean of their tone ratings, returned as a method data
# frame (subid plus one rating column) ready for compare_methods() and track_method().
#   weights:      data frame with subid, tone, and weight (e.g. from preference_weights()
#                 or tier_weights()); weights are rescaled to sum to 1 per respondent
#   label, fill:  attributes used for plot labels and colors
#   rating_name:  name of the rating column
#   tone_ratings: data frame with subid, tone, rating. Defaults to `tone_means`
weighted_method <- function(weights, label, fill = "steelblue",
                            rating_name = "weighted_rating", tone_ratings = tone_means) {
  out <- tone_ratings |>
    inner_join(select(weights, subid, tone, weight), by = c("subid", "tone")) |>
    summarise(rating = sum(weight * rating) / sum(weight), .by = subid)
  names(out)[2] <- rating_name
  attr(out, "label") <- label
  attr(out, "fill") <- fill
  out
}

# Score a grid of tuning settings for the individualized weighted methods, each with no
# drop, after dropping the least-preferred tone, and after dropping the two
# least-preferred tones. Returns one row per setting with the tracker metrics
# (method, mean, sd, weighted_opt, weighted_dis) plus family, param, and drop.
#   grid: data frame with family, param, and drop, where
#         family "Weighted individualized": param = offset subtracted from the preference
#                score (weights proportional to pref - offset)
#         family "Tier-weighted":           param = ratio between consecutive tiers
#         family "Power-weighted":          param = power applied to (pref - 1)
#         drop: "none", "low", or "two"
#   prefs: subid, tone, pref;  kept_low / kept_two: subid, tone (tones kept after each drop)
#   min_share: smallest share of messages the least-seen tone should get. Two columns
#         report it: min_share_median (the median respondent's least-seen tone share) and
#         pct_meets_min (share of respondents whose least-seen tone gets at least
#         min_share). The least-seen tone is the one with the smallest weight among the
#         tones the method delivers (after any drop), so a tone the weighting drives to 0
#         counts as 0.
tune_weighted_methods <- function(grid, prefs, kept_low, kept_two, tone_ratings = tone_means,
                                  min_share = 0.10) {
  prefs_by_drop <- list(
    none = prefs,
    low = semi_join(prefs, kept_low, by = c("subid", "tone")),
    two = semi_join(prefs, kept_two, by = c("subid", "tone")))
  param_name <- c("Weighted individualized" = "offset", "Tier-weighted" = "ratio",
                  "Power-weighted" = "power")
  drop_suffix <- c(none = "", low = " + drop low", two = " + drop two")

  pmap(grid, \(family, param, drop, ...) {
    p <- prefs_by_drop[[drop]]
    w <- switch(family,
      "Weighted individualized" = preference_weights(p, offset = param),
      "Tier-weighted" = tier_weights(p, ratio = param),
      "Power-weighted" = preference_weights(p, offset = 1, power = param),
      stop("Unknown family: ", family))
    label <- paste0(family, " (", param_name[[family]], " = ", param, ")", drop_suffix[[drop]])
    method <- weighted_method(w, label, tone_ratings = tone_ratings)
    least_seen <- w |> summarise(least = min(weight), .by = subid)
    track_method(NULL, method, weights = w, tone_ratings = tone_ratings) |>
      mutate(min_share_median = median(least_seen$least),
             pct_meets_min = mean(least_seen$least >= min_share - 1e-9)) |>
      mutate(family = family, param = param, drop = drop, .before = 1)
  }) |>
    list_rbind()
}

# Tone weights for the "data-driven" method. Acknowledging is dropped for everyone, and
# each respondent's preferences among the remaining four tones decide their split. Rules
# are applied in this order, and a respondent gets the first rule they meet:
#   1. Straightliner (all four tones tied):            SE 40, VA 20, Legit 20, Norms 20
#   2. Norms in the highest preference tier:           SE 30, VA 20, Legit 20, Norms 30
#   3. Self efficacy and Value affirmation tied:       SE 40, VA 40, Legit 20, Norms 0
#   4. Value affirmation preferred over Self efficacy: VA 50, SE 25, Legit 25, Norms 0
#   5. Self efficacy preferred over Value affirmation: SE 50, VA 25, Legit 25, Norms 0
# (SE = self efficacy, VA = value affirmation, Legit = legitimizing)
#   prefs: data frame with subid, tone, and pref (preference score for that tone)
# Returns subid, tone, weight (including acknowledging at 0), and the rule applied.
# Respondents missing a preference for any of the four tones are left out.
data_driven_weights <- function(prefs) {
  rule_weights <- tibble::tribble(
    ~rule,                                    ~self_efficacy, ~value_affirmation, ~legitimizing, ~norms,
    "Straightliner (all 4 tones tied)",       .40,            .20,                .20,           .20,
    "Norms in highest tier",                  .30,            .20,                .20,           .30,
    "Self efficacy = Value affirmation",      .40,            .40,                .20,           0,
    "Value affirmation above Self efficacy",  .25,            .50,                .25,           0,
    "Self efficacy above Value affirmation",  .50,            .25,                .25,           0)

  prefs |>
    filter(tone %in% c("self_efficacy", "value_affirmation", "legitimizing", "norms")) |>
    pivot_wider(names_from = tone, values_from = pref) |>
    drop_na() |>
    mutate(rule = case_when(
      self_efficacy == value_affirmation & value_affirmation == legitimizing &
        legitimizing == norms ~ "Straightliner (all 4 tones tied)",
      norms == pmax(self_efficacy, value_affirmation, legitimizing, norms) ~ "Norms in highest tier",
      self_efficacy == value_affirmation ~ "Self efficacy = Value affirmation",
      value_affirmation > self_efficacy ~ "Value affirmation above Self efficacy",
      .default = "Self efficacy above Value affirmation")) |>
    select(subid, rule) |>
    left_join(rule_weights, by = "rule") |>
    pivot_longer(c(self_efficacy, value_affirmation, legitimizing, norms),
                 names_to = "tone", values_to = "weight") |>
    bind_rows(
      prefs |> distinct(subid) |> mutate(tone = "acknowledging", weight = 0)) |>
    mutate(rule = rule[!is.na(rule)][1], .by = subid) |>
    filter(!is.na(rule))
}

# ---------------------------------------------------------------------------
# Helpers for the tone preference report (scripts/reports/report_prefs.qmd)
# ---------------------------------------------------------------------------

# Add each respondent's highest- and lowest-preferred tone(s) and a straightliner flag.
#   pref_top, pref_bottom: list columns of the tone(s) tied for the highest / lowest
#                          preference score (ties kept)
#   pref_straightline:     TRUE when all preference scores are identical
add_pref_extremes <- function(panel,
                              pref_cols = c("pref_legitimizing", "pref_norms",
                                            "pref_value_affirmation",
                                            "pref_self_efficacy", "pref_acknowledging")) {
  extreme_tones <- function(..., fn) {
    x <- c(...)
    if (all(is.na(x))) return(character(0))
    str_remove(names(x)[which(x == fn(x, na.rm = TRUE))], "^pref_")
  }

  panel |>
    mutate(
      pref_top = pmap(pick(all_of(pref_cols)), extreme_tones, fn = max),
      pref_bottom = pmap(pick(all_of(pref_cols)), extreme_tones, fn = min),
      pref_straightline = pmap_dbl(pick(all_of(pref_cols)), \(...) sd(c(...))) == 0)
}

# subid of respondents with `tone` in their highest (end = "top") or lowest
# (end = "bottom") preference tier, ties included. Straightliners are excluded
# unless exclude_straightliners = FALSE.
pref_group_ids <- function(panel, tone, end = c("top", "bottom"),
                           exclude_straightliners = TRUE) {
  end <- match.arg(end)
  panel |>
    filter(map_lgl(.data[[paste0("pref_", end)]], \(x) tone %in% x),
           !exclude_straightliners | !pref_straightline) |>
    pull(subid)
}

# Box plots of mean message ratings across tones, one panel per group laid out side by
# side. Within each panel, tones run from lowest to highest mean rating (left to right),
# so the order can differ between panels. Panel labels show n, and x-axis labels are
# angled so they are not cut off.
#   groups:  named list of subid vectors; names label the panels
#   ratings: data frame with subid, tone, rating
#   colors:  named fill colors by tone
plot_ratings_by_groups <- function(groups, ratings, colors) {
  data <- imap(groups, \(ids, nm) {
    ratings |>
      filter(subid %in% ids, !is.na(rating)) |>
      mutate(group = paste0(nm, " (n = ", length(ids), ")"))
  }) |>
    list_rbind() |>
    mutate(tone = as.character(tone),
           group = factor(group, levels = unique(group)),
           # tone + panel, so each panel can sort its own tones by mean rating
           tone_panel = fct_reorder(paste(tone, group, sep = "___"), rating, mean))

  ggplot(data, aes(x = tone_panel, y = rating, fill = tone)) +
    geom_boxplot(show.legend = FALSE) +
    stat_summary(fun = mean, geom = "point", shape = 23, size = 2, fill = "white") +
    stat_summary(fun = mean, geom = "text",
                 aes(label = round(after_stat(y), 2)), vjust = -1) +
    facet_wrap(~group, nrow = 1, scales = "free_x") +
    scale_fill_manual(values = colors) +
    scale_x_discrete(labels = \(x) str_to_sentence(str_replace(str_remove(x, "___.*"), "_", " "))) +
    scale_y_continuous(limits = c(1, 7), breaks = 1:7) +
    labs(x = "Tone", y = "Mean Message Rating") +
    theme(axis.text.x = element_text(angle = 35, hjust = 1),
          plot.margin = margin(5.5, 5.5, 5.5, 20))
}

# Box plots of mean message ratings across tones for respondents with `tone` in their
# lowest preference tier (left) vs. their highest preference tier (right). Ties are
# included, and straightliners are excluded. Uses plot_ratings_by_groups().
#   tone:    tone name, e.g. "self_efficacy"
#   panel:   has subid, pref_top, pref_bottom, and pref_straightline
#   ratings: data frame with subid, tone, rating
plot_ratings_by_tier <- function(tone, panel, ratings, colors) {
  label <- str_to_sentence(str_replace(tone, "_", " "))
  groups <- list(
    pref_group_ids(panel, tone, "bottom"),
    pref_group_ids(panel, tone, "top"))
  names(groups) <- paste(label, c("in lowest preference tier", "in highest preference tier"))
  plot_ratings_by_groups(groups, ratings, colors)
}
