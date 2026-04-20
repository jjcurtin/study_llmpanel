# setup chtc jobs & associated files/folders

library(tidyverse) 
algorithm <- "glmnet"
source("https://github.com/jjcurtin/lab_support/blob/main/chtc/fun_make_jobs.R?raw=true")
path_training_controls <- here::here(str_c("_chtc/training_controls_panel_", 
                                           algorithm,
                                           ".R"))
make_jobs(path_training_controls, overwrite_batch = FALSE)
