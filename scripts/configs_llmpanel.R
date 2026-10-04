# Feature specs and standard configurations for rec_llmpanel()
# Source before functions_llmpanel.R. Requires tidyverse.
# See scripts/eda/6_panel_recipes.qmd for the design rationale.

# Algorithms supported by rec_llmpanel(algorithm = ...)
llmpanel_algorithms <- c("glmnet", "xgboost", "ranger")

# Per-algorithm preprocessing in rec_llmpanel()
#   dummy:        "treatment" (reference level dropped), "one_hot" (all levels
#                 kept), or "none" (nominal features stay as factors)
#   nzv:          step_nzv() on interaction columns
#   normalize:    step_normalize() on all predictors
#   interactions: whether explicit interaction terms are supported
# ranger splits factors natively (set respect.unordered.factors = "order" in
# the model spec), and one-hot columns would inflate how often multi-level
# factors are sampled by mtry. step_interact() needs numeric columns, so
# explicit interactions are not supported when nominal features stay factors.
llmpanel_algorithm_prep <- tibble::tribble(
  ~algorithm, ~dummy,      ~nzv,  ~normalize, ~interactions,
  "glmnet",   "treatment", TRUE,  TRUE,       TRUE,
  "xgboost",  "one_hot",   FALSE, FALSE,      TRUE,
  "ranger",   "none",      FALSE, FALSE,      FALSE
)

# Predictors included in every recipe
llmpanel_controls <- c("q1_legitimizing_1", "q2_self_efficacy_1", "q3_acknowledging_1",
                       "q4_value_affirmation_1", "q5_norms_1", "q6_formality_1",
                       "context", "style", "tone", "survey_version")
llmpanel_dem_constant <- c("dem_sex", "dem_race", "dem_orientation", "dem_n_household")

# One row per variable used by each feature option: the variable, how it is
# encoded, and the term it contributes to step_interact() (NA = not used in
# interactions).
# Dummy selectors exclude "_x_" so later interaction steps don't pick up
# interaction columns created by earlier steps (which would add unrequested
# higher-order terms).
# The "+adjusted" income options add household-adjusted income alongside the
# bracket; interactions use only the bracket, the bracket dummy selector
# excludes dem_income_adjusted, and Income x Household Size is not available.
llmpanel_feature_specs <- tibble::tribble(
  ~feature,    ~option,            ~var,                  ~encoding,         ~int_term,
  "age",       "numeric",          "dem_age",             "numeric",         "dem_age",
  "age",       "nominal",          "dem_age_binned",      "nominal_ordered", 'matches("^dem_age_binned_(?!.*_x_)", perl = TRUE)',
  "age",       "ordinal",          "dem_age_binned",      "ordinal",         "dem_age_binned",
  "education", "ordinal",          "dem_education",       "ordinal",         "dem_education",
  "education", "nominal",          "dem_edu_collapsed",   "nominal",         'matches("^dem_edu_collapsed_(?!.*_x_)", perl = TRUE)',
  "income",    "nominal",          "dem_income",          "nominal_ordered", 'matches("^dem_income_(?!.*_x_)", perl = TRUE)',
  "income",    "ordinal",          "dem_income",          "ordinal",         "dem_income",
  "income",    "adjusted",         "dem_income_adjusted", "numeric",         "dem_income_adjusted",
  "income",    "nominal+adjusted", "dem_income",          "nominal_ordered", 'matches("^dem_income_(?!adjusted)(?!.*_x_)", perl = TRUE)',
  "income",    "nominal+adjusted", "dem_income_adjusted", "numeric",         NA,
  "income",    "ordinal+adjusted", "dem_income",          "ordinal",         "dem_income",
  "income",    "ordinal+adjusted", "dem_income_adjusted", "numeric",         NA
)

llmpanel_age_options <- c("numeric", "nominal", "ordinal")
llmpanel_education_options <- c("ordinal", "nominal")
llmpanel_income_options <- c("nominal", "ordinal", "adjusted",
                             "nominal+adjusted", "ordinal+adjusted")

# Interactions available to rec_llmpanel(dem_interactions = ...)
llmpanel_dem_interactions <- c("age_income_education", "sex_race_orientation",
                               "age_household", "income_household")

# Interactions available to rec_llmpanel(base_interactions = ...)
#   attitudes_tone:  each of q1-q5 x message tone
#   formality_style: q6 formality preference x message style
llmpanel_base_interactions <- c("attitudes_tone", "formality_style")

# Per-algorithm defaults, used when an argument is left NULL in rec_llmpanel().
# Trees find cutpoints and interactions themselves, so xgboost defaults to
# scored income and no explicit interaction terms.
llmpanel_algorithm_defaults <- list(
  glmnet  = list(age = "numeric", education = "ordinal", income = "nominal",
                 dem_interactions = "all", base_interactions = "all"),
  xgboost = list(age = "numeric", education = "ordinal", income = "ordinal",
                 dem_interactions = "none", base_interactions = "none"),
  ranger  = list(age = "numeric", education = "ordinal", income = "ordinal",
                 dem_interactions = "none", base_interactions = "none"))
#----------------------------------------------------------------------------

# Short config label from feature options
llmpanel_config_label <- function(age, education, income) {
  paste0("age", substr(age, 1, 3),
         "_edu", substr(education, 1, 3),
         "_", c(nominal = "incnom", ordinal = "incord", adjusted = "adjinc",
                "nominal+adjusted" = "incnom_adj",
                "ordinal+adjusted" = "incord_adj")[income])
}

# Standard configurations. Pass the argument columns to rec_llmpanel() with
# purrr::pmap() and the matching `algorithm`; `config` is a short label for
# naming recipes. Interactions are not part of the grids and follow the
# algorithm defaults unless set in the pmap() call
# (e.g. dem_interactions = "none").

# GLMnet: 30 feature combinations, all interactions by default
glmnet_configs <- tidyr::expand_grid(
  age = llmpanel_age_options,
  education = llmpanel_education_options,
  income = llmpanel_income_options) |>
  dplyr::mutate(config = llmpanel_config_label(age, education, income))

# XGBoost: raw age and 6-level education score (trees choose their own
# cutpoints), varying only how income is represented. Adjusted income is a
# ratio with household size, which trees can only approximate with splits, so
# it is worth offering directly. No explicit interactions by default.
xgb_configs <- tidyr::expand_grid(
  age = "numeric",
  education = "ordinal",
  income = c("ordinal", "adjusted", "ordinal+adjusted")) |>
  dplyr::mutate(config = llmpanel_config_label(age, education, income))

# Random forest (ranger): same feature options as XGBoost for the same
# reasons; differs only in preprocessing (nominal features stay factors).
# Kept as a separate grid so the two can diverge.
rf_configs <- tidyr::expand_grid(
  age = "numeric",
  education = "ordinal",
  income = c("ordinal", "adjusted", "ordinal+adjusted")) |>
  dplyr::mutate(config = llmpanel_config_label(age, education, income))
