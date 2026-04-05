library(tidyverse)
library(tidymodels)

# open training data on server
source("https://github.com/jjcurtin/lab_support/blob/main/format_path.R?raw=true")
version_eda <- "v7"  # to avoid conflict with training controls version
path_in <- format_path(str_c("llmpanel/chtc/train_", version_eda, "/input"))
fn <- here::here(path_in, "data_trn.csv")  
d <- read_csv(fn, show_col_types = FALSE) |> 
  glimpse()



# REMEMBER TO RESOURCE TRAINING CONTROLS WITH EVERY EDIT!
# THEN SET UP CONFIG AND RUN FORMAT, AND RECIPE BELOW
config <- tibble(
  algorithm = "glmnet",
  feature_set = "pref"
)
d2 <- format_data(d)  |> # d2 to avoid need to re-read d
  glimpse()

rec <- build_recipe(d = d2, config = config)
rec_prep <- rec |> 
  prep(training = d2)

feat <- rec_prep |> 
  bake(new_data = NULL) |> 
  glimpse()

names(feat)
