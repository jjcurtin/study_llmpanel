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

format_eda <- function (d){
  
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
# highest-rated tone on the preferences survey (ties included) is `top_tone`.
# `panel` has subid, the list column pref_top, and the logical pref_straightline;
# `ratings` has subid, tone, rating. Straightliners are excluded.
plot_ratings_by_pref_top <- function(top_tone, panel, ratings, colors) {
  top_label <- str_replace(top_tone, "_", " ")

  ids <- panel |>
    filter(map_lgl(pref_top, \(x) top_tone %in% x), !pref_straightline) |>
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
                           " rated highest on preferences (n = ", length(ids),
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
