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
      across(c(context, style, tone, survey_version, dem_orientation), factor))
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
    rec <- rec |> step_dummy(context, style, tone, survey_version, dem_orientation,
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
      sex_race_orientation = '~ (dem_sex + dem_race + matches("^dem_orientation_(?!.*_x_)", perl = TRUE))^3',
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
