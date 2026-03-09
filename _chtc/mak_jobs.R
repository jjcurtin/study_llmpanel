# setup chtc jobs & associated files/folders

library(tidyverse) 
source("https://github.com/jjcurtin/lab_support/blob/main/chtc/fun_make_jobs.R?raw=true")
path_training_controls <- here::here("modeling/chtc/training_controls_optimize.R")
make_jobs(path_training_controls, overwrite_batch = FALSE)
