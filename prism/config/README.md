# Required files

## script_pipeline.csv
"script_path","arguments","enabled"
- script_path is relative to the scripts directory
- arguments should be formatted as arg1 arg2 separated by spaces
- enabled is a boolean

## study_coordinators.csv
"name","phone_number"
- name is any
- phone_number should be formatted as a 10 digit phone number

## study_participants.csv
"unique_id","last_name","first_name","on_study","phone_number","ema_time","ema_reminder_time","feedback_time","feedback_reminder_time"
- unique_id is any
- last_name is any
- first_name is any
- on_study is yes or no
- phone_number should be formatted as a 10 digit phone number
- ema_time is military time in HH:MM:SS format
- ema_reminder_time is military time in HH:MM:SS format
- feedback_time is military time in HH:MM:SS format
- feedback_reminder_time is military time in HH:MM:SS format

## system_task_schedule.csv
"task_type","task_time","run_today"
- task_type must be in the format TASK_TYPE and must match a file in the tasks folder in the format _task_type.py
  and the class inside must be of the format TaskType
- task_time is military time in HH:MM:SS format
- run_today is a boolean