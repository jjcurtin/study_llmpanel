# Training controls for LLMPanel study for GLMNET

# version 1: first version
# version 2: corrected problem with feature selection for the three configurations
# version 3: change hyperparameters to better tune models
# version 4: more hyperparameter tuning
# version 7: switched to one hot encoding for non-binary categorical variables
# version 8: scaled numeric predictors
# version 9: limited scaling to numeric predictors
# version 10: re-start with baseline glmnet 

# NOTES------------------------------
source("https://github.com/jjcurtin/lab_support/blob/main/format_path.R?raw=true")

# SET GLOBAL PARAMETERS--------------------
version <- "v10"
algorithm <- "glmnet"  # glmnet, random_forest, xgboost

# ordinal_nominal
# ordinal = c(numeric, onehot, target)
# nominal = c(onehot, target)
feature_set <- c("numeric_onehot")

seed_splits <- 102030
ml_mode <- "regression"   # regression or classification
configs_per_job <- 100 

# CHTC SPECIFIC CONTROLS----------------------------
username <- "jjcurtin" # for setting staging directory (until we have group staging folder)
stage_data <- FALSE # If FALSE .sif will still be staged, just not data_trn
max_idle <- 1000
request_cpus <- 1 
request_memory <- "2000MB"
request_disk <- "1000MB" # <- tune the memory and disk
want_campus_pools <- TRUE 
want_ospool <- TRUE 

# OUTCOME-------------------------------------
y_col_name <- "message_rating" 

resample <- "none" # no resampling; regression problem

# CV SETTINGS---------------------------------
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

# STUDY PATHS----------------------------
# the name of the batch of jobs to set folder name
name_batch <- str_c("train_", version) 

# the path to the batch of jobs to put the folder name
path_batch <- format_path(str_c("llmpanel/chtc/", name_batch)) 

# location of data set
path_data <- format_path("llmpanel/data_processed/")
data_trn <- "panel_long.csv"

# ALGORITHM-SPECIFIC HYPERPARAMETERS-----------
hp1_glmnet <- seq(0, 1, by = .1) # alpha (mixture)
hp2_glmnet_min <- -8 # min for penalty grid - will be passed into c(0, exp(seq(min, max, length.out = out)))
hp2_glmnet_max <- 0 # max for penalty grid
hp2_glmnet_out <- 200 # length of penalty grid

# FORMAT DATA-----------------------------------------
format_data <- function (d){
  d <- d |> 
    rename(y = message_rating, 
           pref_legitimizing = q1_legitimizing,
           pref_self_efficacy = q2_self_efficacy,
           pref_acknowledging = q3_acknowledging,
           pref_value_affirmation = q4_value_affirmation,
           pref_norms = q5_norms,
           pref_formality = q6_formality)
}
  

# BUILD RECIPE---------------------------------------
# Script should have a single build_recipe function to be compatible with fit script. 
build_recipe <- function(d, config) {
  # d: (training) dataset from which to build recipe
  # config: single-row job-specific tibble
  
  # get relevant info from config (algorithm, feature_set, resample, under_ratio)
  algorithm <- config$algorithm
  feature_set <- config$feature_set
  
  # Set recipe steps generalizable to all model configurations for GLMNET
  # include recode of y to numeric
  rec <- recipe(y ~ ., data = d) |> 
    step_mutate(y = case_when(
      y == "strongly_disagree" ~ 1,
      y =="disagree" ~ 2,
      y == "somewhat_disagree" ~ 3,
      y == "neutral" ~ 4,
      y == "somewhat_agree" ~ 5,
      y == "agree" ~ 6,
      y == "strongly_agree" ~ 7,
      .default = NA_real_
   )) |> 
   step_rm(subid, survey_version, context)
  
  rec <- rec |> 
    # consider each of these removals
    step_rm(contains(c("identity", "text", "input")), 
           dem_student, dem_n_household, dem_minority,
           dem_race_multiple)
    step_zv(all_predictors()) |> 
    step_impute_median(all_numeric_predictors()) |>  
    step_impute_mode(all_nominal_predictors())
    
  # dummy for all binary categorical
  # done for all configurations
  # UPDATE TO LIST ALL BINARY PREDICTORS
  rec <- rec |> 
    step_dummy(all_nominal_predictors(), one_hot = FALSE) 
   
  #------------------------------------------------------------------------ 
  # Configs for ordinal predictors 
  # handle ordinal predictors as numeric 
  if (str_detect(feature_set, "^ordinal_")) {
    q_cols <- c(
      "pref_legitimizing",
      "pref_self_efficacy",
      "pref_acknowledging",
      "pref_value_affirmation",
      "pref_norms"
    )
  
    rec <- rec |>   
      step_mutate(across(all_of(q_cols)),
        ~ recode_values(
          .x,
          "strongly_disagree" ~ 1,
          "disagree"          ~ 2,
          "somewhat_disagree" ~ 3,
          "neutral"           ~ 4,
          "somewhat_agree"    ~ 5,
          "agree"             ~ 6,
          "strongly_agree"    ~ 7
        )
      ) |> 
      step_mutate(pref_formality = case_when(
        pref_formality == "strongly_prefer_informal" ~ 1,
        pref_formality == "moderately_prefer_informal" ~ 2,
        pref_formality == "slightly_prefer_informal" ~ 3,
        pref_formality == "neutral" ~ 4,
        pref_formality == "slightly_prefer_formal" ~ 5,
        pref_formality == "moderately_prefer_formal" ~ 6,
        pref_formality == "strongly_prefer_formal" ~ 7
      )) |> 
      step_mutate(dem_education = case_when(
        dem_education == "high_school_or_ged" ~ 1,
        dem_education == "some_college" ~ 2,
        dem_education == "2-year_degree" ~ 3,
        dem_education == "4-year_degree" ~ 4,
        dem_education == "advanced_degree" ~ 5
      )) |> 
      step_mutate(dem_income = case_when(
        dem_income == "Less than $25,000" ~ 1,
        dem_income == "$25,000 - $37,499" ~ 2,
        dem_income == "$37,500 - $49,999" ~ 3,
        dem_income == "$50,000 - $74,999" ~ 4,
        dem_income == "$75,000 - $99,999" ~ 5,
        dem_income == "$100,000 - $149,999" ~ 6,
        dem_income == "$150,000 - $199,999" ~ 7,
        dem_income == "$200,000 or more" ~ 8
      ))
  }
 
  
  if (str_detect(feature_set, "^onehot_")) {
    # NEED TO UPDATE
  }
  if (str_detect(feature_set, "^target_")) {
    # NEED TO UPDATE
  }
 
  
# --------------------------------------------------------------------------
  # handle nominal configs
  
  
# --------------------------------------------------------------------------
  # finish last steps 
  # add interactions 
  rec <- rec |>   
    step_interact(terms = ~ matches("^tone_(legitimizing|norms|value_affirmation|self_efficacy|acknowledging)$"):starts_with("dem_")) |> 
    step_interact(terms = ~ matches("^style_informal$"):starts_with("dem_"))
    step_interact(terms = ~ matches("^tone_(legitimizing|norms|value_affirmation|self_efficacy|acknowledging)$"):starts_with("pref_")) |> 
    step_interact(terms = ~ matches("^style_informal$"):starts_with("pref_")) 
     
  # final steps 
  rec <- rec |> 
    # drop columns with NA values after imputation (100% NA)
    step_rm(where(~ any(is.na(.)))) |> 
    step_nzv(all_predictors()) |>
    # consider standardizing only numeric predictors in a later version
    step_normalize(matches(c("pref_", "dem_age", "dem_education", "dem_income"))) 
  
  return(rec)
}