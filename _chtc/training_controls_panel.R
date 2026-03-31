# Training controls for LLMPanel study

# NOTES------------------------------
source("https://github.com/jjcurtin/lab_support/blob/main/format_path.R?raw=true")

# SET GLOBAL PARAMETERS--------------------
version <- "v1"
algorithm <- "xgboost"  # glmnet, random_forest, xgboost
feature_set <- c("base", "dem", "pref")
seed_splits <- 102030
ml_mode <- "regression"   # regression or classification
configs_per_job <- 50

# CHTC SPECIFIC CONTROLS----------------------------
username <- "jjcurtin" # for setting staging directory (until we have group staging folder)
stage_data <- FALSE # If FALSE .sif will still be staged, just not data_trn
max_idle <- 1000
request_cpus <- 1 
request_memory <- "10000MB"
request_disk <- "2000MB" # <- tune the memory and disk
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
hp1_xgboost <- c(0.000001, 0.00001, 0.0001, 0.001, 0.01)  # learn_rate
hp2_xgboost <-  c(1, 2, 3, 4) # tree_depth
hp3_xgboost <-  seq(2, 30, by = 2)  # mtry <- note: will change
# trees = 500 (included in fit function by default)
# early stopping = 20 (included in fit function by default)
 

# FORMAT DATA-----------------------------------------
format_data <- function (d){
  d <- d |> 
    rename(y = message_rating) |> 
    mutate(y = case_when(
      y == "strongly_disagree" ~ 1,
      y =="disagree" ~ 2,
      y == "somewhat_disagree" ~ 3,
      y == "neutral" ~ 4,
      y == "somewhat_agree" ~ 5,
      y == "agree" ~ 6,
      y == "strongly_agree" ~ 7,
      .default = NA_real_
    ))
  
  
  # also make the message preferences numeric
  q_cols <- c(
    "q1_legitimizing",
    "q2_self_efficacy",
    "q3_acknowledging",
    "q4_value_affirmation",
    "q5_norms"
  )
  
  for (col in intersect(q_cols, names(d))) {
    d[[col]] <- case_when(
      d[[col]] == "strongly_disagree" ~ 0,
      d[[col]] == "disagree" ~ 1,
      d[[col]] == "somewhat_disagree" ~ 2,
      d[[col]] == "neutral" ~ 3,
      d[[col]] == "somewhat_agree" ~ 4,
      d[[col]] == "agree" ~ 5,
      d[[col]] == "strongly_agree" ~ 6,
      .default = NA_real_
    )
  }
  
  # and formality
  d <- d |> 
    mutate(q6_formality = case_when(
      q6_formality == "strongly_prefer_informal" ~ 1,
      q6_formality == "moderately_prefer_informal" ~ 2,
      q6_formality == "slightly_prefer_informal" ~ 3,
      q6_formality == "neutral" ~ 4,
      q6_formality == "slightly_prefer_formal" ~ 5,
      q6_formality == "moderately_prefer_formal" ~ 6,
      q6_formality == "strongly_prefer_formal" ~ 7,
      .default = NA_real_
    ))
}
  

# BUILD RECIPE---------------------------------------
# Script should have a single build_recipe function to be compatible with fit script. 
build_recipe <- function(d, config) {
  # d: (training) dataset from which to build recipe
  # config: single-row job-specific tibble
  
  # get relevant info from config (algorithm, feature_set, resample, under_ratio)
  algorithm <- config$algorithm
  feature_set <- config$feature_set
 
  
  # NOTE: Tmp remove of dem_orientation.  consider adding again with step_novel 
  d <- d |> 
    select(-subid, -dem_identity, -contains("other_text"), -dem_race_multiple, -dem_student,
           -dem_n_household, -dem_minority, -q7_user_input, -survey_version,
           -context, -dem_orientation)
  
  


  # COLIN: income and education are ordinal and can be engineered with single feature here
  d <- d |> 
    mutate(dem_education = case_when(
      dem_education == "high_school_or_ged" ~ 1,
      dem_education == "some_college" ~ 2,
      dem_education == "2-year_degree" ~ 3,
      dem_education == "4-year_degree" ~ 4,
      dem_education == "advanced_degree" ~ 5,
      .default = NA_real_
    )) |> 
    mutate(dem_income = case_when(
      dem_income == "Less than $25,000" ~ 1,
      dem_income == "$25,000 - $37,499" ~ 2,
      dem_income == "$37,500 - $49,999" ~ 3,
      dem_income == "$50,000 - $74,999" ~ 4,
      dem_income == "$75,000 - $99,999" ~ 5,
      dem_income == "$100,000 - $149,999" ~ 6,
      dem_income == "$150,000 - $199,999" ~ 7,
      dem_income == "$200,000 or more" ~ 8,
      .default = NA_real_
    ))

  
  # Set recipe steps generalizable to all model configurations
  rec <- recipe(y ~ ., data = d)

  rec <- rec |> 
    step_zv(all_predictors()) |> 
    step_impute_median(all_numeric_predictors()) |>  
    step_impute_mode(all_nominal_predictors()) 

  
  # base model features
  if (str_detect(feature_set, "base")) {
    d <- d |> 
      select(y, tone, style) 
  }
  
  
  # dem model features
  if (str_detect(feature_set, "dem")) {
    d <- d |> 
      select(y, tone, style, starts_with("dem_")) 
  }
  
 
  
  if (algorithm == "random_forest") {
    # no algorithm specific steps
  } 
  
  if (algorithm == "xgboost") {
    rec <- rec  |>  
      step_dummy(all_nominal_predictors(), one_hot = FALSE) 
  } 
  
  # final steps for all algorithms
  rec <- rec |> 
    # drop columns with NA values after imputation (100% NA)
    step_rm(where(~ any(is.na(.)))) |> 
    step_nzv(all_predictors())
  
  return(rec)
}
