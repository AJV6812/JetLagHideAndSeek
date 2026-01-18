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
    This is the exception that is raised if the hiders ask a question while one is already active.
    """
