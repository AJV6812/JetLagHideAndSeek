"""
This file is for any custom interfaces that have to exist.
"""

from abc import ABC, abstractmethod
import configparser

par = configparser.ConfigParser()
par.read("hide_and_seek.cfg")

DEFAULT_ALLOCATED_QUESTION_TIME = par.getint("MASTER", "DEFAULT_ALLOCATED_QUESTION_TIME")

class Card(ABC):
    """
    This is an abstract class that represents a card. Each card type will have its own
    implementation.
    """


class Question(ABC):
    """
    This is an abstract class that represents a question. Each question type will implement
    this separately, and each specific question will implement that question type
    """

    @abstractmethod
    def __str__(self) -> str:
        """
        :return: Question that can be displayed to the user
        :rtype: str
        """

    @abstractmethod
    def get_allocated_time(self) -> int:
        """
        Gets the amount of time the hider is allocated to answer this question
        
        :param self: This object
        :return: The number of seconds to answer
        :rtype: int
        """
        return DEFAULT_ALLOCATED_QUESTION_TIME

    def __eq__(self, other) -> bool:
        #TODO: Implement
        return str(self) == str(other)

class StandardQuestion(Question):
    """
    This is an abstract class that represents a non-thermometer question.
    """

class Frontend(ABC):
    """
    This is the abstract class that represents any frontend.
    """
