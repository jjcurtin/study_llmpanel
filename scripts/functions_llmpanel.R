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

# GLMnet data prep and recipe builder
# Requires tidyverse and tidymodels to be loaded before calling the functions.
# See scripts/eda/6_panel_recipes.qmd for the design rationale.

# Predictors included in every GLMnet recipe
glmnet_controls <- c("q1_legitimizing_1", "q2_self_efficacy_1", "q3_acknowledging_1",
                     "q4_value_affirmation_1", "q5_norms_1", "q6_formality_1",
                     "context", "style", "tone", "survey_version")
glmnet_dem_constant <- c("dem_sex", "dem_race", "dem_orientation", "dem_n_household")

# One row per feature option: the variable it uses, how it is encoded,
# and the term it contributes to step_interact().
# Dummy selectors exclude "_x_" so later interaction steps don't pick up
# interaction columns created by earlier steps (which would add unrequested
# higher-order terms).
glmnet_feature_specs <- tibble::tribble(
  ~feature,    ~option,    ~var,                  ~encoding,         ~int_term,
  "age",       "numeric",  "dem_age",             "numeric",         "dem_age",
  "age",       "nominal",  "dem_age_binned",      "nominal_ordered", 'matches("^dem_age_binned_(?!.*_x_)", perl = TRUE)',
  "age",       "ordinal",  "dem_age_binned",      "ordinal",         "dem_age_binned",
  "education", "ordinal",  "dem_education",       "ordinal",         "dem_education",
  "education", "nominal",  "dem_edu_collapsed",   "nominal",         'matches("^dem_edu_collapsed_(?!.*_x_)", perl = TRUE)',
  "income",    "nominal",  "dem_income",          "nominal_ordered", 'matches("^dem_income_(?!.*_x_)", perl = TRUE)',
  "income",    "ordinal",  "dem_income",          "ordinal",         "dem_income",
  "income",    "adjusted", "dem_income_adjusted", "numeric",         "dem_income_adjusted"
)

# Interactions available to rec_glmnet_build(interactions = ...)
glmnet_interactions <- c("age_income_education", "sex_race_orientation",
                         "age_household", "income_household")

# The 60 standard configurations (30 main effects, 30 with all interactions).
# Pass the argument columns to rec_glmnet_build() with purrr::pmap();
# `config` is a short label for naming recipes.
glmnet_configs <- tidyr::expand_grid(
  age = c("numeric", "nominal", "ordinal"),
  education = c("ordinal", "nominal"),
  income = c("nominal", "ordinal", "adjusted"),
  income_adjusted = c(FALSE, TRUE),
  interactions = c("none", "all")) |>
  dplyr::filter(!(income == "adjusted" & income_adjusted)) |>
  dplyr::mutate(config = paste0(
    "age", substr(age, 1, 3),
    "_edu", substr(education, 1, 3),
    "_", ifelse(income == "adjusted", "adjinc", paste0("inc", substr(income, 1, 3))),
    ifelse(income_adjusted, "_adj", ""),
    ifelse(interactions == "all", "_int", "")))
#----------------------------------------------------------------------------

# Convert pivoted panel_long (with engineered demographic features) to GLMnet-ready data
prep_glmnet_data <- function(data) {
  required <- c("message_rating", glmnet_controls, glmnet_dem_constant,
                unique(glmnet_feature_specs$var))
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
rec_glmnet_base <- function(data, dem_adjustable) {
  rec_formula <- reformulate(
    c("subid", glmnet_controls, glmnet_dem_constant, dem_adjustable),
    response = "message_rating")

  recipe(rec_formula, data = data) |>
    update_role(subid, new_role = "id") |>
    step_ordinalscore(matches("^q[1-6]_")) |>
    step_dummy(context, style, tone, survey_version, dem_orientation)
}
#----------------------------------------------------------------------------

# Build a GLMnet recipe from feature options
#   data:            output of prep_glmnet_data()
#   age:             "numeric", "nominal" (binned, dummy coded), or "ordinal" (binned, scored)
#   education:       "ordinal" (6 levels, scored) or "nominal" (collapsed to 3, dummy coded)
#   income:          "nominal" or "ordinal" income bracket, or "adjusted" to use
#                    household-adjusted income in place of the bracket
#   income_adjusted: TRUE adds household-adjusted income alongside the income bracket
#   interactions:    "none", "all", or any subset of glmnet_interactions
rec_glmnet_build <- function(data,
                             age = c("numeric", "nominal", "ordinal"),
                             education = c("ordinal", "nominal"),
                             income = c("nominal", "ordinal", "adjusted"),
                             income_adjusted = FALSE,
                             interactions = "none") {
  age <- match.arg(age)
  education <- match.arg(education)
  income <- match.arg(income)

  if (!is.logical(income_adjusted) || length(income_adjusted) != 1 || is.na(income_adjusted)) {
    stop("`income_adjusted` must be TRUE or FALSE.")
  }
  if (income == "adjusted" && income_adjusted) {
    stop("`income_adjusted = TRUE` adds adjusted income alongside the income bracket, ",
         "so it requires `income = \"nominal\"` or `\"ordinal\"`.")
  }

  # Income x Household Size is not used with adjusted income, which already
  # incorporates household size
  available_ints <- if (income == "adjusted") {
    setdiff(glmnet_interactions, "income_household")
  } else {
    glmnet_interactions
  }
  if (identical(interactions, "all")) {
    interactions <- available_ints
  } else if (identical(interactions, "none") || length(interactions) == 0) {
    interactions <- character(0)
  } else {
    unknown <- setdiff(interactions, glmnet_interactions)
    if (length(unknown) > 0) {
      stop("Unknown interaction(s): ", paste(unknown, collapse = ", "),
           ". Use \"none\", \"all\", or any of: ", paste(glmnet_interactions, collapse = ", "), ".")
    }
    if (!all(interactions %in% available_ints)) {
      stop("\"income_household\" is not available with `income = \"adjusted\"`.")
    }
  }

  specs <- dplyr::bind_rows(
    glmnet_feature_specs[glmnet_feature_specs$feature == "age" &
                           glmnet_feature_specs$option == age, ],
    glmnet_feature_specs[glmnet_feature_specs$feature == "education" &
                           glmnet_feature_specs$option == education, ],
    glmnet_feature_specs[glmnet_feature_specs$feature == "income" &
                           glmnet_feature_specs$option == income, ],
    if (income_adjusted) {
      tibble::tibble(feature = "income_adjusted", option = "added",
                     var = "dem_income_adjusted", encoding = "numeric", int_term = NA_character_)
    })
  vars_with <- \(enc) specs$var[specs$encoding %in% enc]

  rec <- rec_glmnet_base(data, specs$var)
  if (length(vars_with("nominal_ordered")) > 0) {
    rec <- rec |> step_unorder(all_of(vars_with("nominal_ordered")))
  }
  if (length(vars_with("ordinal")) > 0) {
    rec <- rec |> step_ordinalscore(all_of(vars_with("ordinal")))
  }
  if (length(vars_with(c("nominal", "nominal_ordered"))) > 0) {
    rec <- rec |> step_dummy(all_of(vars_with(c("nominal", "nominal_ordered"))))
  }

  if (length(interactions) > 0) {
    term_for <- \(feat) specs$int_term[specs$feature == feat]
    age_term <- term_for("age")
    edu_term <- term_for("education")
    inc_term <- term_for("income")
    # Keep dem_income_adjusted out of the income-bracket dummy selector
    if (income == "nominal" && income_adjusted) {
      inc_term <- 'matches("^dem_income_(?!adjusted)(?!.*_x_)", perl = TRUE)'
    }

    int_formulas <- c(
      age_income_education = paste0("~ (", age_term, " + ", inc_term, " + ", edu_term, ")^3"),
      sex_race_orientation = '~ (dem_sex + dem_race + matches("^dem_orientation_(?!.*_x_)", perl = TRUE))^3',
      age_household = paste0("~ ", age_term, ":dem_n_household"),
      income_household = paste0("~ ", inc_term, ":dem_n_household"))
    # Fixed order keeps output columns consistent regardless of argument order
    for (f in int_formulas[intersect(glmnet_interactions, interactions)]) {
      rec <- rec |> step_interact(terms = !!as.formula(f))
    }
    rec <- rec |> step_nzv(contains("_x_"))
  }

  rec |>
    step_zv(all_predictors()) |>
    step_normalize(all_predictors())
}
#----------------------------------------------------------------------------
