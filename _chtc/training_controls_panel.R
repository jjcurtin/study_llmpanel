# Training controls for EMA study

# NOTES------------------------------
options(conflicts.policy = "depends.ok")
library(stringr, exclude = "fixed")
library(dplyr)
library(recipes)
source("https://github.com/jjcurtin/lab_support/blob/main/format_path.R?raw=true")

# SET GLOBAL PARAMETERS--------------------
version <- "v1"
algorithm <- "glmnet"  # glmnet, random_forest, xgboost
feature_set <- c("base", "demo", "pref")
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
hp1_glmnet <- seq(0, 1, length.out = 11) # alpha (mixture)
hp2_glmnet_min <- -8 # min for penalty grid - will be passed into exp(seq(min, max, length.out = out))
hp2_glmnet_max <- 2 # max for penalty grid
hp2_glmnet_out <- 200 # length of penalty grid
# 
# hp1_knn <- seq(5, 255, length.out = 26) # neighbors (must be integer)
# 
hp1_rf <- c(2, 10, 20, 30, 40) # mtry (p/3 for reg or square root of p for class)
hp2_rf <- c(2, 15, 30) # min_n
hp3_rf <- 1500 # trees (10 x's number of predictors)

#hp1_xgboost <- c(0.000001, 0.00001, 0.0001, 0.001, 0.01)  # learn_rate
hp1_xgboost <- c(.001, .01, 0.1, .33, .67, 1)  # learn_rate
#hp2_xgboost <-  c(1, 2, 3, 4, 5, 6, 7) # tree_depth
hp2_xgboost <-  c(1, 2, 3) # tree_depth
#hp3_xgboost <-  seq(50, 300, by = 50)  # mtry
hp3_xgboost <-  seq(33, 200, by = 33)  # mtry <- note: will change
# trees = 500 (included in fit function by default)
# early stopping = 20 (included in fit function by default)
 

# FORMAT DATA-----------------------------------------
format_data <- function (df){
  
  # df <- df |>  
  #   rename(y = !!y_col_name)
  
  # make y numeric
  df <- df |> 
    mutate(y = case_when(
      message_rating == "Strongly Disagree" ~ 0,
      message_rating == "Disagree" ~ 1,
      message_rating == "Somewhat Disagree" ~ 2,
      message_rating == "Neutral" ~ 3,
      message_rating == "Somewhat Agree" ~ 4,
      message_rating == "Agree" ~ 5,
      message_rating == "Strongly Agree" ~ 6,
      .default = NA_real_))
  
  # also make the message preferences numeric
  q_cols <- c(
    "q1_legitimizing",
    "q2_self_efficacy",
    "q3_acknowledging",
    "q4_value_affirmation",
    "q5_norms"
  )
  
  for (col in intersect(q_cols, names(df))) {
    df[[col]] <- case_when(
      df[[col]] == "Strongly Disagree" ~ 0,
      df[[col]] == "Disagree" ~ 1,
      df[[col]] == "Somewhat Disagree" ~ 2,
      df[[col]] == "Neutral" ~ 3,
      df[[col]] == "Somewhat Agree" ~ 4,
      df[[col]] == "Agree" ~ 5,
      df[[col]] == "Strongly Agree" ~ 6,
      .default = NA_real_
    )
  }
  
  # and formality
  df <- df |> 
    mutate(q6_formality = case_when(
      q6_formality == "Strongly Prefer Informal" ~ 0,
      q6_formality == "Moderately Prefer Informal" ~ 1,
      q6_formality == "Slightly Prefer Informal" ~ 2,
      q6_formality == "Neutral" ~ 3,
      q6_formality == "Slightly Prefer Formal" ~ 4,
      q6_formality == "Moderately Prefer Formal" ~ 5,
      q6_formality == "Strongly Prefer Formal" ~ 6,
      .default = NA_real_
    ))
  
  df <- df |> 
    select(-audit_score, -tone_order, -context, 
           -survey_version, -q_total_duration, -message_rating, -q7_user_input, -dem_income)
  

  # pref model uses all features so no need to remove
  
  return(df)
}


# BUILD RECIPE---------------------------------------
# Script should have a single build_recipe function to be compatible with fit script. 
build_recipe <- function(d, config) {
  # d: (training) dataset from which to build recipe
  # config: single-row job-specific tibble
  
  # get relevant info from config (algorithm, feature_set, resample, under_ratio)
  algorithm <- config$algorithm
  feature_set <- config$feature_set
  
  # use tidyverse (rather than recipe) for selection because its easier
  if (str_detect(config$feature_set, "base")) {
    d <- d |> 
      select(subid, y, tone, style) 
  }
  if (str_detect(config$feature_set, "demo")) {
    d <- d |> 
      select(subid, y, tone, style, starts_with("dem_")) 
  }
  
  # Set recipe steps generalizable to all model configurations
  rec <- recipe(y ~ ., data = d) |> 
    step_rm(subid)  # needed to retain until now for grouped CV in splits

  rec <- rec |> 
    step_impute_median(all_numeric_predictors()) |>  
    step_impute_mode(all_nominal_predictors()) 
  
  # this is where we'll do additional recipe steps that are feature dependent
  # but we don't have them yet

  #if (str_detect(feature_set, "valaro")) {
    #rec <- rec |> 
      #step_rm(contains("ema_na")) |> 
      #step_rm(contains("ema_pa")) 
  #}
  
  
  # algorithm specific steps
  if (algorithm == "glmnet") {
    rec <- rec  |> 
      step_zv(all_predictors()) |> 
      step_normalize(all_numeric_predictors()) |> 
      step_dummy(all_nominal_predictors(), 
                 one_hot = TRUE) 
  } 
  
  if (algorithm == "random_forest") {
    # no algorithm specific steps
  } 
  
  if (algorithm == "xgboost") {
    rec <- rec  |>  
      step_dummy(all_nominal_predictors(), one_hot = TRUE) 
  } 
  
  # final steps for all algorithms
  rec <- rec |> 
    # drop columns with NA values after imputation (100% NA)
    step_rm(where(~ any(is.na(.)))) |> 
    step_nzv(all_predictors())
  
  return(rec)
}
