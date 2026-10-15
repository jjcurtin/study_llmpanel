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


# SET GLOBAL PARAMETERS---------------------------------------------------------
version <- "v11"
algorithm <- "glmnet"  # glmnet, random_forest, xgboost

# CONFIGURATIONS ---------------------------------------------------------------
# ordinal_nominal
# ordinal = c(numeric, onehot, target)
# nominal = c(onehot, target)
feature_set <- c("numeric_onehot")

# ML PARAMETERS ----------------------------------------------------------------
ml_mode <- "regression"   # regression or classification
resample <- "none" # no resampling; regression problem
y_col_name <- "message_rating" 

# CHTC SPECIFIC CONTROLS----------------------------
configs_per_job <- 100 # used for batching configs within CHTC jobs
username <- "jjcurtin" # for setting staging directory (until we have group staging folder)
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
data_trn <- "panel_long.csv"

# ALGORITHM-SPECIFIC HYPERPARAMETERS--------------------------------------------
hp1_glmnet <- seq(0, 1, by = .1) # alpha (mixture)
hp2_glmnet_min <- -8 # min for penalty grid - will be passed into c(0, exp(seq(min, max, length.out = out)))
hp2_glmnet_max <- 0 # max for penalty grid
hp2_glmnet_out <- 200 # length of penalty grid

# FORMAT DATA-------------------------------------------------------------------
format_data <- function (d){
  d <- d |> 
    rename(y = message_rating, 
           pref_legitimizing = q1_legitimizing,
           pref_self_efficacy = q2_self_efficacy,
           pref_acknowledging = q3_acknowledging,
           pref_value_affirmation = q4_value_affirmation,
           pref_norms = q5_norms,
           pref_formality = q6_formality) |> 
    mutate(dem_orientation2 = if_else(dem_orientation == "straight", "straight", "other")) |> 
    select(-dem_orientation, -dem_orientation_other_text)
  
  # get numeric options for ordinal predictors
  # will choose among them in recipe
  # for recoding in recipe below   
  q_cols <- c(
    "pref_legitimizing_ord",
    "pref_self_efficacy_ord",
    "pref_acknowledging_ord",
    "pref_value_affirmation_ord",
    "pref_norms_ord"
  )
  
  d <- d |>
    mutate(pref_legitimizing_ord = pref_legitimizing,
           pref_self_efficacy_ord = pref_self_efficacy,
           pref_acknowledging_ord = pref_acknowledging,
           pref_value_affirmation_ord = pref_value_affirmation,
           pref_norms_ord = pref_norms) |>
    mutate(across(all_of(q_cols), # preferences
      ~ recode_values(
        .x,
        "strongly_disagree" ~ 1,
        "disagree"          ~ 2,
        "somewhat_disagree" ~ 3,
        "neutral"           ~ 4,
        "somewhat_agree"    ~ 5,
        "agree"             ~ 6,
        "strongly_agree"    ~ 7))) |> 
    mutate(pref_formality_ord = recode_values(
      pref_formality,
      "strongly_prefer_informal"   ~ 1,
      "moderately_prefer_informal" ~ 2,
      "slightly_prefer_informal"   ~ 3,
      "neutral"                    ~ 4,
      "slightly_prefer_formal"     ~ 5,
      "moderately_prefer_formal"   ~ 6,
      "strongly_prefer_formal"     ~ 7)) |>
    mutate(dem_education_ord = recode_values(
      dem_education,
      "high_school_or_ged" ~ 1,
      "some_college"       ~ 2,
      "2-year_degree"      ~ 3,
      "4-year_degree"      ~ 4,
      "advanced_degree"    ~ 5)) |>
    mutate(dem_income_ord = recode_values(
      dem_income,
      "Less than $25,000"     ~ 1,
      "$25,000 - $37,499"     ~ 2,
      "$37,500 - $49,999"     ~ 3,
      "$50,000 - $74,999"     ~ 4,
      "$75,000 - $99,999"     ~ 5,
      "$100,000 - $149,999"   ~ 6,
      "$150,000 - $199,999"   ~ 7,
      "$200,000 or more"      ~ 8))
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
    step_mutate(y = recode_values(
      y,
      "strongly_disagree" ~ 1,
      "disagree"          ~ 2,
      "somewhat_disagree" ~ 3,
      "neutral"           ~ 4,
      "somewhat_agree"    ~ 5,
      "agree"             ~ 6,
      "strongly_agree"    ~ 7)) |> 
   step_rm(subid, survey_version, context, contains(c("identity", "text", "input")), 
           dem_student, dem_n_household, dem_minority, dem_race_multiple) |> 
    step_zv(all_predictors()) |> 
    step_impute_median(all_numeric_predictors()) |>  
    step_impute_mode(all_nominal_predictors())
    
  # dummy always used for binary categorical across all configs to avoid 2 features
  rec <- rec |> 
    step_dummy(dem_sex, dem_orientation2, dem_hispanic, matches("^dem_race"), 
               one_hot = FALSE) 
   
  #----------------------------------------------------------------------------- 
  # Configs for ordinal predictors ---------------------------------------------
  
  # handle ordinal predictors as numeric 
  if (str_detect(feature_set, "^ordinal_")) {
 
    # rm cols that begin with pref and dont end with ord 
    # and education and incomes
    rec <- rec |>   
      step_rm(matches("^pref_(?!.*_ord$)", perl = TRUE)) |>  
      step_rm(dem_education, dem_income)
  }
 
  
  # handle ordinal predictors with onehot 
  if (str_detect(feature_set, "^onehot_")) {
    
    # NEED TO UPDATE
    
    # rm cols that end with ord 
    # and education and incomes
    rec <- rec |>   
      step_rm(matches("_ord$")) 
  }
  
  
  # handle ordinal predictors with target encoding
  if (str_detect(feature_set, "^target_")) {
    # NEED TO UPDATE
  }
 
  
  # ----------------------------------------------------------------------------
  # Configs for multi-level nominal predictors ---------------------------------
  
  # handle nominal predictors with onehot 
  # UPDATE TO HANDLE RACE HERE FOR ONE HOT AND BELOW FOR TARGET
  # WILL NEED TO CALCULATE SINGLE RACE VARIABLE IN FORMAT DATA  
  if (str_detect(feature_set, "_onehot$")) {
    rec <- rec |> 
      step_dummy(tone, style, dem_marital_status, 
                 one_hot = TRUE) 
  }
  
  # handle nominal predictors with target encoding
  if (str_detect(feature_set, "_target$")) {
    # NEED TO UPDATE
  }
  
  # ----------------------------------------------------------------------------
  # add interactions -----------------------------------------------------------
  # UPDATE - DOES THIS NEED TO CHANGE BASED ON HOW WE HANDLE CATEGORICAL PREDICTORS?
  # rec <- rec |>   
  #   step_interact(terms = ~ matches("^tone_(legitimizing|norms|value_affirmation|self_efficacy|acknowledging)$"):starts_with("dem_")) |> 
  #   step_interact(terms = ~ matches("^style_informal$"):starts_with("dem_"))
  #   step_interact(terms = ~ matches("^tone_(legitimizing|norms|value_affirmation|self_efficacy|acknowledging)$"):starts_with("pref_")) |> 
  #   step_interact(terms = ~ matches("^style_informal$"):starts_with("pref_")) 
  
  # ----------------------------------------------------------------------------
  # standardize ONLY numeric predictors -----------------------------------------------------------
    
  # UPDATE - HOW TO DO THIS BASED ON CONFIG
  rec <- rec |> 
    # consider standardizing only numeric predictors in a later version
    step_normalize(matches(c("pref_", "dem_age", "dem_education", "dem_income"))) 
       
  # ----------------------------------------------------------------------------
  # finish last steps-----------------------------------------------------------
  
  # final steps 
  rec <- rec |> 
    # drop columns with NA values after imputation (100% NA)
    step_rm(where(~ any(is.na(.)))) |> 
    step_nzv(all_predictors())
  
  return(rec)
}