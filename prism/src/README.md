# Directory
## run_prism.py
- Runs PRISM server, serves flask app via Waitress
- Test mode has hot reloading for all modules meaning new modules can be added while server is running
- Prod mode notifies coordinators about system task failures and sends sms to participants
## prism_interface.py
- Connects to PRISM server on local machine port 5000, can be used to change current study data or shut down process.
## tasks/
- Contains various tasks that are loaded by the main PRISM application for selection and use during runtime.