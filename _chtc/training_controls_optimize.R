# Training controls for EMA study

# NOTES------------------------------
# version 1: daily labels, 4x EMA, demos, 24h rolls
# version 2: daily labels, 1x EMA, demos,  24h rolls
# version 3: daily labels, 1x EMA, GPS data set, 24h rolls
# version 4: daily labels, 1x EMA, GPS & demo features, 24h rolls
# version 5: day window, 1 hr rolls, 1x EMA, GPS, & demo features
# version 6: Added stratify (incorrectly), EMA abstinence question, monthly features 
#            dropped transit and location variance features
#            dropped 12 and 24 hour period features for EMA b/c using only 1x daily
# version 7: fixed issue with stratify, removed monthly diff features, switched to 3x10
#            increased tree depth, mtry and decreased learn rate
# version 8: returned to 4x EMA (+ abstinence).  stratify by h/l, raw monthly, 
#            gps (all features except transit), and demo features; 
#            changed to simple 6x5
# version 9: Changed to 1x EMA.  All other features the same (excepted fixed issue
#            with GPS features for other types with spaces in names).  Changed to 5x5 CV
#            changed mtry to 50:300 by 50
# version 10: Restried to just 1x EMA (stratified).  Drop GPS, monthly, and demos
# version 11: Changed to 1x EMA for 24HOUR rolls.  Included GPS, monthly.   stratified
#             keeping all features matched to v9 for fair comparison (but did drop demos)
# version 12: Switched to logistic.  dropped no, neutral and ema min features
# version 13: Switched to GLMNet and back to 1 hour rolls.  Dropped no and neutral 
#             from GPS.  Dropped min from EMA. 
# version 14: Same features as v13 but back to XGBoost
# version 15: repeat of v13 with correction to sample size!
# version 16: same features as v15 but switch to xgboost.  (repeat of v14 with correct nrows)
# version 17: fix issue with feature set selection.  Handle feature rename at this stage
#             All else same as v15
# version 18: drops monthly. Includes on gps, ema and strat as per previous versions
#             also didnt run dif only model to save time.   Its not good
# version 19: switch to one-hot codes for day of week and na/pa  
# version 20: update feature names
# version 21: back to 24 hour rolls.  features with and without nzv
# version 22: put in na/pa features for 24hr rolls.  Only using rm nzc configs
# version 23: selected down to p168 and p24/0 for gps/ema. Also not scaling binary features
# version 24: same as 23 but with XGBoost
# version 25: same as 24 with XGBoost but different hyperparameter options
# version 26: back to glmnet with with lin/quad on val/arousal instead of pa/na

library(stringr)
library(dplyr)
source("https://github.com/jjcurtin/lab_support/blob/main/format_path.R?raw=true")

# SET GLOBAL PARAMETERS--------------------
# study <- "opt" # not needed because only training one model for optimize
version <- "v26"
algorithm <- "glmnet"  # glmnet, random_forest, glm, xgboost
feature_set <- c("raw_valaro", "raw_valaro_poly2", "raw_pana", "raw_pana_poly2") # EMA Features set names.  Did not include "dif"
seed_splits <- 102030
ml_mode <- "classification"   # regression or classification
configs_per_job <- 50 # reduced from 50 to 10 for 1 hour rolls bc took almost 2 days.  Back to 50 for 24 hour rolls

# RESAMPLING FOR OUTCOME-----------------------------------
# note that ratio is under_ratio, which is used by downsampling as is
# It is converted to  overratio (1/ratio) for up and smote
resample <- c("up_5", "up_4", "up_3", "up_2", "up_1", "down_5", "down_4", "down_3", "down_2", "down_1") 


# CHTC SPECIFIC CONTROLS----------------------------
username <- "jjcurtin" # for setting staging directory (until we have group staging folder)
stage_data <- FALSE # If FALSE .sif will still be staged, just not data_trn
max_idle <- 1000
request_cpus <- 1 
request_memory <- "50000MB" # 50000MB with 1 hour rolls.  Dropped to 20000MB for 24 hour rolls
request_disk <- "3000MB"
want_campus_pools <- TRUE 
want_ospool <- TRUE 

# OUTCOME-------------------------------------
y_col_name <- "lapse" 
y_level_pos <- "lapse" 
y_level_neg <- "no lapse"


# CV SETTINGS---------------------------------
cv_resample_type <- "kfold" # can be boot, kfold, or nested
cv_resample = "6_x_5" # can be repeats_x_folds (e.g., 1_x_10, 10_x_10) or number of bootstraps (e.g., 100)
cv_inner_resample <- NULL # can also be a single number for bootstrapping (i.e., 100)
cv_outer_resample <- NULL # outer resample will always be kfold
cv_group <- "subid" # set to NULL if not grouping
cv_strat <- TRUE 

cv_name <- if_else(cv_resample_type == "nested",
                   str_c(cv_resample_type, "_", cv_inner_resample, "_",
                         cv_outer_resample),
                   str_c(cv_resample_type, "_", cv_resample))

# STUDY PATHS----------------------------
# the name of the batch of jobs to set folder name
name_batch <- str_c("train_", version) 

# the path to the batch of jobs to put the folder name
path_batch <- format_path(str_c("optimize/chtc/", name_batch)) 

# location of data set
path_data <- format_path("optimize/data_processed/features")
data_trn <- str_c("features_", version, ".csv")  

# ALGORITHM-SPECIFIC HYPERPARAMETERS-----------
hp1_glmnet <- c(0, seq(.1, 1, length.out = 11)) # alpha (mixture)
hp2_glmnet_min <- -8 # min for penalty grid - will be passed into exp(seq(min, max, length.out = out))
hp2_glmnet_max <- 2 # max for penalty grid
hp2_glmnet_out <- 200 # length of penalty grid
# 
# hp1_knn <- seq(5, 255, length.out = 26) # neighbors (must be integer)
# 
# hp1_rf <- c(2, 10, 20, 30, 40) # mtry (p/3 for reg or square root of p for class)
# hp2_rf <- c(2, 15, 30) # min_n
# hp3_rf <- 1500 # trees (10 x's number of predictors)

#hp1_xgboost <- c(0.000001, 0.00001, 0.0001, 0.001, 0.01)  # learn_rate
hp1_xgboost <- c(.001, .01, 0.1, .33, .67, 1)  # learn_rate
#hp2_xgboost <-  c(1, 2, 3, 4, 5, 6, 7) # tree_depth
hp2_xgboost <-  c(1, 2, 3) # tree_depth
#hp3_xgboost <-  seq(50, 300, by = 50)  # mtry
hp3_xgboost <-  seq(33, 200, by = 33)  # mtry
# trees = 500 (included in fit function by default)
# early stopping = 20 (included in fit function by default)
 

# FORMAT DATA-----------------------------------------
format_data <- function (df){
  
  df |>  
    select(-c(dttm_label)) |> 
    rename(y = !!y_col_name) |>  
    mutate(y = factor(y, levels = c(!!y_level_pos, !!y_level_neg)), # set pos class first
           across(where(is.character), factor)) 
}


# BUILD RECIPE---------------------------------------
# Script should have a single build_recipe function to be compatible with fit script. 
build_recipe <- function(d, config) {
  # d: (training) dataset from which to build recipe
  # config: single-row job-specific tibble
  
  # get relevant info from config (algorithm, feature_set, resample, under_ratio)
  algorithm <- config$algorithm
  feature_set <- config$feature_set
  
  if (config$resample == "none") {
    resample <- config$resample
  } else {
    resample <- str_split(config$resample, "_")[[1]][1]
    ratio <- as.numeric(str_split(config$resample, "_")[[1]][2])
  }
  
  # Set recipe steps generalizable to all model configurations
  rec <- recipe(y ~ ., data = d) |> 
    step_rm(subid)  # needed to retain until now for grouped CV in splits

  if(cv_strat) {
    rec <- rec |>
      step_rm(strat) # remove strat variable
  }

  rec <- rec |> 
    step_impute_median(all_numeric_predictors()) |>  
    step_impute_mode(all_nominal_predictors()) 
  
  # handle feature set selection
  # no selection needed if "all"
  if (str_detect(feature_set, "raw")) {
    rec <- rec |> 
      step_rm(contains("dif")) 
  }
  if (str_detect(feature_set, "dif")) {
    rec <- rec |> 
      step_rm(contains("raw")) 
  }
    
  # resampling options for unbalanced outcome variable
  if (resample == "down") {
    rec <- rec |>  
      # ratio is equivalent to tidymodels under_ratio
      themis::step_downsample(y, under_ratio = ratio, seed = 10) 
  }
  
  if (resample == "smote") {
    ratio <- 1 / ratio # correct ratio to over_ratio
    rec <- rec |>  
      themis::step_smote(y, over_ratio = ratio, seed = 10) 
  }
  
  if (resample == "up") {
    ratio <- 1 / ratio # correct ratio to over_ratio
    rec <- rec |>  
      themis::step_upsample(y, over_ratio = ratio, seed = 10)
  }

  

  # handle pana vs. valaro features and poly2
  if (str_detect(feature_set, "valaro")) {
    rec <- rec |> 
      step_rm(contains("ema_na")) |> 
      step_rm(contains("ema_pa")) 
  }
  if (str_detect(feature_set, "pana")) {
    rec <- rec |> 
      step_rm(contains("ema_6")) |> 
      step_rm(contains("ema_7")) 
  }
  
  if (str_detect(feature_set, "poly2")) {
    
    if (str_detect(feature_set, "valaro")) {
      rec <- rec |> 
        step_poly(contains("ema_6"), degree = 2) |>
        step_poly(contains("ema_7"), degree = 2)
    }
    if (str_detect(feature_set, "pana")) {
      rec <- rec |> 
        step_poly(contains("ema_na"), degree = 2) |>
        step_poly(contains("ema_pa"), degree = 2)
    }
  } 
  
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
  
  if (algorithm == "glm") {
    rec <- rec  |> 
      step_dummy(all_nominal_predictors(), 
                 one_hot = TRUE) |> 
      step_zv(all_predictors()) |> 
      step_normalize(all_predictors())
  } 
  
  if (algorithm == "xgboost") {
    rec <- rec  |>  
      step_zv(all_predictors()) |> 
      step_normalize(all_numeric_predictors()) |> # done for later interpretation of categories
      step_dummy(all_nominal_predictors(), one_hot = TRUE) 
  } 
  
  # final steps for all algorithms
  rec <- rec |> 
    # drop columns with NA values after imputation (100% NA)
    step_rm(where(~ any(is.na(.)))) |> 
    step_nzv(all_predictors())
  
  return(rec)
}