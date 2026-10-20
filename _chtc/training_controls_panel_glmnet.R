# Training controls for LLMPanel study for GLMNET

# NOTES-------------------------------------------------------------------------
# version 1: first version
# version 2: corrected problem with feature selection for the three configurations
# version 3: change hyperparameters to better tune models
# version 4: more hyperparameter tuning
# version 7: switched to one hot encoding for non-binary categorical variables
# version 8: scaled numeric predictors
# version 9: limited scaling to numeric predictors
# version 10: dropped zero variance on message ratings
# version 11: re-start with baseline glmnet 
# version 12: glmnet with final reduced sample (Andrew)


# SET GLOBAL PARAMETERS---------------------------------------------------------
version <- "v12"
algorithm <- "glmnet"  # glmnet, random_forest, xgboost

# CONFIGURATIONS ---------------------------------------------------------------
# Two recipes: education as ordinal or collapsed categorical.
# All other feature options (age, income) are constant across configs.
feature_set <- c("edu_ordinal", "edu_collapsed")

# ML PARAMETERS ----------------------------------------------------------------
ml_mode <- "regression"   # regression or classification
resample <- "none" # no resampling; regression problem
y_col_name <- "message_rating" 

# CHTC SPECIFIC CONTROLS----------------------------
configs_per_job <- 100 # used for batching configs within CHTC jobs
username <- "a/aksanford" # for setting staging directory (until we have group staging folder)
stage_data <- FALSE # If FALSE .sif will still be staged, just not data_trn
max_idle <- 1000
request_cpus <- 1 
request_memory <- "2000MB"
request_disk <- "1000MB" # <- tune the memory and disk
want_campus_pools <- TRUE 
want_ospool <- TRUE 

# CV SETTINGS-------------------------------------------------------------------
seed_splits <- 102030
cv_resample_type <- "nested" # can be boot, kfold, or nested
cv_resample = NULL # can be repeats_x_folds (e.g., 1_x_10, 10_x_10) or number of bootstraps (e.g., 100)
cv_inner_resample <- "2_x_5" # can also be a single number for bootstrapping (i.e., 100)
cv_outer_resample <- "6_x_5" # outer resample will always be kfold
cv_group <- "subid" # set to NULL if not grouping
cv_strat <- FALSE 

cv_name <- if_else(cv_resample_type == "nested",
                   str_c(cv_resample_type, "_", cv_inner_resample, "_",
                         cv_outer_resample),
                   str_c(cv_resample_type, "_", cv_resample))

# BATCH INFO--------------------------------------------------------------------
source("https://github.com/jjcurtin/lab_support/blob/main/format_path.R?raw=true")

# the name of the batch of jobs to set folder name
name_batch <- str_c("train_", version) 

# the path to the batch of jobs to put the folder name
path_batch <- format_path(str_c("llmpanel/chtc/", name_batch)) 

# location of data set for the batch
path_data <- format_path("llmpanel/data_processed/")
data_trn <- "panel.csv"

# ALGORITHM-SPECIFIC HYPERPARAMETERS--------------------------------------------
hp1_glmnet <- seq(0, 1, by = .1) # alpha (mixture)
hp2_glmnet_min <- -8 # min for penalty grid - will be passed into c(0, exp(seq(min, max, length.out = out)))
hp2_glmnet_max <- 0 # max for penalty grid
hp2_glmnet_out <- 200 # length of penalty grid

# FORMAT DATA-------------------------------------------------------------------
format_data <- function (d){
  
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
                  ~ recode_values(
                    .x,
                    "strongly_disagree" ~ 1,
                    "disagree"          ~ 2,
                    "somewhat_disagree" ~ 3,
                    "neutral"           ~ 4,
                    "somewhat_agree"    ~ 5,
                    "agree"             ~ 6,
                    "strongly_agree"    ~ 7))) |>
    
    # Numericize formality scale
    mutate(
      pref_formality = recode_values(
        pref_formality,
        "strongly_prefer_informal"   ~ 1,
        "moderately_prefer_informal" ~ 2,
        "slightly_prefer_informal"   ~ 3,
        "neutral"                    ~ 4,
        "slightly_prefer_formal"     ~ 5,
        "moderately_prefer_formal"   ~ 6,
        "strongly_prefer_formal"     ~ 7),
      
      # Numericize income scale
      dem_income = recode_values(
        dem_income,
        "Less than $25,000"   ~ 12500,   # Midpoint estimates for each bracket
        "$25,000 - $37,499"   ~ 31250,
        "$37,500 - $49,999"   ~ 43750,
        "$50,000 - $74,999"   ~ 62500,
        "$75,000 - $99,999"   ~ 87500,
        "$100,000 - $149,999" ~ 125000,
        "$150,000 - $199,999" ~ 175000,
        "$200,000 or more"    ~ 250000), # The cap for this one is debatable
      
      # Household-adjust income
      dem_income = dem_income / sqrt(dem_n_household),
      
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
           -contains("race"), -dem_marital_status, -dem_minority,
           -dem_identity, -dem_n_household, -dem_student, contains("_hi_"),
           contains("_hd_"), contains("_li_"), -contains("timing")) |>
    
    # Pivot long format
    pivot_longer(
      cols= `x1_hi_1_fl_1`:`x4_li_10_in_1`,
      values_to = "y",
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
        substr(tone_style, 2, 2) == "v" ~ "value_affirmation")) |>
    
    select(-q_num, -tone_style, -context, -survey_version) |>
    
    # Numericize outcome variable (y)
    
    mutate(
      y = recode_values(
        y,
        "strongly_disagree" ~ 1,
        "disagree"          ~ 2,
        "somewhat_disagree" ~ 3,
        "neutral"           ~ 4,
        "somewhat_agree"    ~ 5,
        "agree"             ~ 6,
        "strongly_agree"    ~ 7)) |> 
    
    # Remove empty rows
    filter(!is.na(y),
           str_trim(y) != "")
}

# BUILD RECIPE------------------------------------------------------------------
# Script should have a single build_recipe function to be compatible with fit script. 
build_recipe <- function(d, config) {
  # d: (training) dataset from which to build recipe
  # config: single-row job-specific tibble

  #----------------------------------------------------------------------------- 
  # setup of constants ---------------------------------------------------------
  algorithm <- config$algorithm
  feature_set <- config$feature_set
 
  #----------------------------------------------------------------------------- 
  # Set recipe steps for all model configurations for GLMNET--------------------
  rec <- recipe(y ~ ., data = d) |>
    step_rm(subid) |> 
    step_zv(all_predictors()) |> 
    step_impute_median(all_numeric_predictors()) |>  
    step_impute_mode(all_nominal_predictors())
    
  # dummy for binary categorical across all configs to avoid 2 features,
  # one-hot for multi-category tone
  rec <- rec |> 
    step_dummy(dem_sex, dem_orientation, dem_ethnicity, style, 
               one_hot = FALSE) |> 
    step_dummy(tone, one_hot = TRUE)
   
  #----------------------------------------------------------------------------- 
  # Configs for education ---------------------------------------------
  
  # Education as ordered factor
  if (str_detect(feature_set, "edu_ordinal")) {
    rec <- rec |>
      step_mutate(
        dem_education = recode_values(
          dem_education,
          "less_than_high_school_or_ged_degree" ~ 1,
          "high_school_or_ged"                  ~ 2,
          "some_college"                        ~ 3,
          "2_year_degree"                       ~ 4,
          "4_year_degree"                       ~ 5,
          "advanced_degree"                     ~ 6))
  }
   
  # Education as collapsed categorical 
  if (str_detect(feature_set, "edu_collapsed")) {
    rec <- rec |> 
      step_mutate(
        dem_education = factor(case_when(
          dem_education %in% c("high_school_or_ged", "less_than_high_school_or_ged_degree") ~ "hs_or_less",
          dem_education == "some_college" ~ "some_college",
          dem_education %in% c("2_year_degree", "4_year_degree", "advanced_degree") ~ "2_year_degree_or_higher"
        ))) |> 
      step_dummy(dem_education, one_hot = TRUE)
  }
   
  # ----------------------------------------------------------------------------
  # add interactions -----------------------------------------------------------

  rec <- rec |>
    # dem_ x tone_ and dem_ x style (exclude existing interaction cols via _x_)
    step_interact(terms = ~ matches("^dem_(?!.*_x_)", perl = TRUE):starts_with("tone_")) |>
    step_interact(terms = ~ matches("^dem_(?!.*_x_)", perl = TRUE):all_of("style_informal")) |>
    # pref_ (except pref_formality) x tone_
    step_interact(terms = ~ matches("^pref_(legitimizing|self_efficacy|acknowledging|value_affirmation|norms)$"):starts_with("tone_")) |>
    # pref_formality x style
    step_interact(terms = ~ all_of("pref_formality"):all_of("style_informal"))
  
  
  
  # ----------------------------------------------------------------------------
 
  # final steps 
  rec <- rec |> 
    # drop columns with NA values after imputation (100% NA)
    step_rm(where(~ any(is.na(.)))) |> 
    step_nzv(all_predictors())
  
  return(rec)
}
