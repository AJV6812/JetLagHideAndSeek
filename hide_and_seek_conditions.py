import enum
import time
from typing import Callable
from task_scheduler import TaskScheduler

scheduler = TaskScheduler()

class Condition(enum.Enum):
    ACTIVEQUESTION=1

def blank():
    pass

class ConditionManager():
    def __init__(self):
        self.conditions:dict[Condition, Callable[[], None]] = {}


    def add_condition(self, condition:Condition, duration: int|None = None, callback: Callable[[], None] = blank):
        assert condition not in self.conditions.keys()
        self.conditions[condition] = callback
        if duration != None:
            scheduler.add_function(int(time.time() + duration), lambda: self.remove_condition(condition))
    
    def has_condition(self, condition: Condition):
        return condition in self.conditions.keys()

    def remove_condition(self, condition: Condition):
        assert condition in self.conditions.keys()
        self.conditions.pop(condition)()

