## Task Manager explanation
- Each task manager has a task queue and runs in a separate thread so that each one can run independent of the others.
- There are generalized methods, such as add_task, remove_task, that all task managers have in common
- Specific task managers, such as the system task manager and participant manager, have additional functionality that is unique to their operation but inherit all of the shared base class attributes and methods

### Queues explanation
- Queues are a first-in-first-out data structure, which means that the tasks will run in the order that they are added.
- This means that we can queue up the data pulldown, then the batch data processing, then pushing to research drive and as long as they are in the same queue they will run in order
- I anticipate that we will need more task queues (to handle Qualtrics api requests, etc.) so I made this abstract