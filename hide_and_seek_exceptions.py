"""
This file holds all exceptions that can be raised by the backend for the frontend to handle.
"""

from abc import ABC

class JetLagException(ABC, Exception):
    """
    This is an abstract class which all other exceptions extend from.
    """

class QuestionActiveException(JetLagException):
    """
    This is the exception that is raised if the seekers ask a question while one is already active.
    """

class HandSizeExceededException(JetLagException):
    """
    This is the exception that is raised if the hider answers a question with an oversized hand.
    """

class CardNotPlayableException(JetLagException):
    """
    This is the exception that is raised if a card is played without satisfying the necessary
    conditions.
    """
