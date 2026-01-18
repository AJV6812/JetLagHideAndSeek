"""This file is a custom event manager"""

import time
from typing import Coroutine, Callable


class TaskScheduler:
    """
    This scheduler is designed to have tasks added to it over time, but for check_tasks to be
    called about once every second
    """
    def __init__(self):
        # TODO Coroutine subtyping
        self.tasks: list[tuple[int, Coroutine]] = []
        self.functions: list[tuple[int, Callable[[], None]]] = []

    async def check_tasks(self):
        """
        Must be called regularly (around once a second) to ensure that all tasks are completed
        and removed as required.
        """
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
        """
        Add a coroutine to the list of tasks to be completed.
        
        :param task_time: The epoch time that the task should be executed at.
        :type task_time: int
        :param task: Coroutine that should be executed at that time.
        :type task: Coroutine
        """
        self.tasks.append((task_time, task))

    def add_function(self, task_time: int, func: Callable[[], None]):
        """
        Add a function to the list of tasks to be completed.
        
        :param task_time: The epoch time that the task should be executed at.
        :type task_time: int
        :param task: Function that should be executed at that time.
        :type task: Function
        """
        self.functions.append((task_time, func))

    def remove_function(self, func: Callable[[], None]):
        """
        If there are any functions matching the passed func in the scheduler, they are all removed.
        
        :param func: A copy of the function that must be removed.
        :type func: Callable[[], None]
        """
        to_delete = []
        for ind, time_func in enumerate(self.functions):
            if time_func[1].__code__.co_code == func.__code__.co_code:
                to_delete.append(ind)

        for item in sorted(to_delete, reverse=True):
            self.functions.pop(item)
