# TASK abstraction format
This is for creating Python tasks. To run an R script, put it in the ../../scripts directory and PRISM will automatically detect it. 

## Location
- tasks directory

## Filename
- must be all lowercase, separated by underscores
- must have a leading underscore at the beginning and have a .py file extension

## run method
- must set `self.task_type` e.g. `self.task_type = "RUN_R_SCRIPT_PIPELINE"`
- must return non zero value on failure, 0 for success

## capabilities
- Will automatically be loaded by PRISM on start
- Every time a task list is requested via interface it reloads the possible tasks into the system
- Tasks are also reloaded before a task is processed and modules are loaded in dynamically
- This means that tasks can be updated while the system is running 