"""
A file that manages all conditions (or status effects) that the game could have.
"""

import enum
import time
from typing import Callable
from task_scheduler import TaskScheduler

scheduler = TaskScheduler()

class Condition(enum.Enum):
    """
    The conditions that are allowed to be applied.
    Active Question is applied when there is a currently ongoing question.
    Hand Lock is applied when the hider cannot modify his hand, but instead must only play or
    discard cards.
    """
    ACTIVEQUESTION = 1
    HAND_LOCK=2


class ConditionManager:
    """
    Class that keeps track of all active conditions on the game.
    """
    def __init__(self):
        self.conditions: dict[Condition, Callable[[], None]] = {}

    def add_condition(
        self,
        condition: Condition,
        duration: int | None = None,
        callback: Callable[[], None] = lambda: None,
    ):
        """
        Add a condition to the game

        :param condition: Condition to add, must not be currently used
        :type condition: Condition
        :param duration: Number of seconds the condition should last for, or none if it should
            last forever.
        :type duration: int | None
        :param callback: Function which should be called when the condition is removed.
        :type callback: Callable[[], None]
        """
        assert condition not in self.conditions
        self.conditions[condition] = callback
        if duration is not None:
            scheduler.add_function(
                int(time.time() + duration), lambda: self.remove_condition(condition)
            )

    def has_condition(self, condition: Condition):
        """
        Whether the game currently has this condition

        :param condition: Condition to check
        :type condition: Condition
        """
        return condition in self.conditions

    def remove_condition(self, condition: Condition):
        """
        Removes a condition

        :param condition: Condition that the game currently has which is to be removed
        :type condition: Condition
        """
        assert condition in self.conditions
        self.conditions.pop(condition)()
