from task_managers._task_manager import TaskManager

class QualtricsAPIManager(TaskManager):
    def __init__(self, app, name = "QualtricsAPIManager"):
        super().__init__(app, name)

    def process_task(self, task):
        task_type = task.get('task_type')
        self.app.add_to_transcript(f"Executing task: {task_type}", "INFO")
        return 0