# This file is a custom event manager

import time
from typing import Coroutine, Callable


# This scheduler is designed to have tasks added to it over time, but for check_tasks to be called
# about once every second
class TaskScheduler:
    def __init__(self):
        # TODO Coroutine subtyping
        self.tasks: list[tuple[int, Coroutine]] = []
        self.functions: list[tuple[int, Callable[[], None]]] = []

    async def check_tasks(self):
        starting_time = time.time()
        for task in self.tasks:
            if starting_time >= task[0]:
                await task[1]

        for func in self.functions:
            if starting_time >= func[0]:
                func[1]()
        self.tasks = [task for task in self.tasks if starting_time < task[0]]
        self.functions = [func for func in self.functions if starting_time < func[0]]

    def add_task(self, task_time: int, task: Coroutine):
        self.tasks.append((task_time, task))

    def add_function(self, task_time: int, func: Callable[[], None]):
        self.functions.append((task_time, func))

