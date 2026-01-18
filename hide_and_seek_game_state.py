"""
This is the main file for managing the hide and seek game state. This code is not aware of
Discord at all and so could be dropped into any system for running Jet Lag whether virtual or
real. However this code is completely responsible for knowing everything important (other than
the player's actual locations) about the game and enforcing as many of the rules as possible. The
rules that are enforced by the system are in enforceable_rules.txt
"""

import time
import enum
import random
import configparser

from task_scheduler import TaskScheduler
from hide_and_seek_conditions import Condition, ConditionManager
from hide_and_seek_exceptions import QuestionActiveException
from hide_and_seek_interfaces import StandardQuestion, Question

par = configparser.ConfigParser()
par.read("hide_and_seek.cfg")

HIDING_TIME = par.getint("MASTER", "HIDING_TIME")
PLANNING_TIME = par.getint("MASTER", "PLANNING_TIME")
MAX_SEEKING_TIME = par.getint("MASTER", "MAX_SEEKING_TIME")

scheduler = TaskScheduler()



class HiderDeck:
    """
    This is a class to keep track of which cards are in the discard, which cards are in the hand
    and which can still be drawn.
    """

    def count_time_bonuses(self) -> int:
        """
        Calculates the time bonus in the hider's hand
        
        :param self: This object
        :return: The number of seconds of time bonuses granted
        :rtype: int
        """
        #TODO: Implement this
        return 0

class InvestigationBook:
    """
    This is a class to keep track of questions that the seekers have asked.
    """

    def __init__(self):
        self.current_question = None

    def get_times_answered(self, question: Question)->int:
        """
        Gets the number of times a question has been answered by the hider this round
        
        :param self: Description
        :param question: Which question to ask about.
        :type question: Question
        :return: Number of times the question has been asked.
        :rtype: int
        """
        #TODO Implement this
        return 0

    def set_current_question(self, question: Question):
        """
        Sets the question that the hider is currently being asked.
        Assumes that the seekers are currently asking a question.
        
        :param question: Question that was just asked
        :type question: Question
        """
        self.current_question = question

    def reward_mult(self, multiplier: int, num_questions: int):
        """
        Sets a reward multiplier for the next few questions. If there is already one active, this
        function multiplies the multipliers over the relevant interval.
        
        :param multiplier: Number of times to receive extra reward
        :type multiplier: int
        :param num_questions: Number of questions extra reward applies to
        :type num_questions: int
        """
        #TODO: Implement this

    def question_answered(self, hider_deck: HiderDeck):
        """
        Called whenever a question is asked to handle the seeker receiving rewards
        
        :param hider_deck: The current hider deck
        :type hider_deck: HiderDeck
        """
        #TODO: Implement this


class State(enum.Enum):
    """
    A class that represents the different states the game can be in.
    """
    INACTIVE = 1
    HIDERPHASE = 2
    SEEKERPHASE = 3
    HIDERDELAY = 4


class GameState:
    """
    This is the main game state interface that the frontend will interact with.
    """

    def __init__(self, start_time: int, players: list[str]):
        self.state = State.INACTIVE
        self.start_time = start_time
        self.players = players
        self.curr_player = ""
        self.investigation_book = InvestigationBook()
        self.hider_deck = HiderDeck()
        self.conditions = ConditionManager()
        self.times: dict[str, int] = {}
        self.hide_time_start:int = 0
        self.delay_start:int = 0
        self.hider_time_bonus:int = 0
        scheduler.add_function(start_time, self.start_round)
        self.next_player = self._get_next_player()

    def start_round(self):
        """
        Converts the game state from inactive to the hiding phase. Resets the investigation book,
        hider deck, condition system, current player name, and sets the scheduler to start the
        seeking phase in due course.
        """
        if self.state == State.INACTIVE:
            scheduler.remove_function(self.start_round)
            self.state = State.HIDERPHASE
            self.investigation_book = InvestigationBook()
            self.hider_deck = HiderDeck()
            self.conditions = ConditionManager()
            self.curr_player = self.next_player
            scheduler.add_function(int(time.time() + HIDING_TIME), self._release_seekers)

    def _release_seekers(self):
        """
        Function is called when the hiding time is up and the seekers are released.
        The frontend is called to let both the seekers and hider know.
        """
        self.state = State.SEEKERPHASE
        self.hide_time_start = int(time.time())
        scheduler.add_function(
            int(time.time() + MAX_SEEKING_TIME), self._max_hiding_time_reached
        )
        self.hider_time_bonus = 0
        # TODO: Inform frontend

    def ask_question(self, question: StandardQuestion):
        """
        Called when the hiders ask a specific question. Can raise QuestionActiveException, if
        there is already a question been asked. If valid, the frontend is called so the hider can
        be informed.
        
        :param question: Question that is being asked, assumed to not be a thermometer
        :type question: StandardQuestion
        """
        if self.conditions.has_condition(
            Condition.ACTIVEQUESTION
        ):  # TODO: Unless active question is a semi-asked thermometer
            raise QuestionActiveException()
        scheduler.add_function(
            int(time.time() + question.get_allocated_time()),
            lambda: self._check_question_answered(
                question, self.investigation_book.get_times_answered(question) + 1
            ),
        )
        self.conditions.add_condition(Condition.ACTIVEQUESTION)
        # TODO: Inform frontend

    def _check_question_answered(self, question: Question, times_answered: int):
        """
        Called once the time limit has been expired 
        
        :param question: Question that must have been answered
        :type question: Question
        :param times_answered: Number of times this question must have been answered by the time
            this function is called
        :type times_answered: int
        """
        if self.investigation_book.get_times_answered(question) < times_answered:
            self.state = State.HIDERDELAY
            self.investigation_book.reward_mult(0, 1)
            self.delay_start = int(time.time())
            self.investigation_book.set_current_question(question)
            # TODO: Inform frontend

    def answered_question(self):
        """
        Called when a question is answered.
        """
        self.conditions.remove_condition(Condition.ACTIVEQUESTION)
        if self.state == State.HIDERDELAY:
            self.state = State.SEEKERPHASE
            self.hider_time_bonus -= int(time.time() - self.delay_start)
            self.investigation_book.question_answered(self.hider_deck)
            # TODO: Inform frontend
        else:
            self.investigation_book.question_answered(self.hider_deck)
            # TODO: Inform frontend

    def hider_caught(self):
        """
        Called when the hider is caught. Tallies the hider's time, and sets the next player.
        """
        self.state = State.INACTIVE
        self.hider_time_bonus += self.hider_deck.count_time_bonuses()
        self.times[self.curr_player] = (
            int(time.time()) - self.hide_time_start + self.hider_time_bonus
        )
        self.next_player = self._get_next_player()
        scheduler.remove_function(self._max_hiding_time_reached)
        scheduler.add_function(int(time.time() + PLANNING_TIME), self.start_round)
        # TODO: Inform frontend

    def _get_next_player(self) -> str:
        unattempted = [x for x in self.players if x not in self.times]
        if len(unattempted) == 0:
            return random.choice(
                [
                    x
                    for x,y in self.times.items()
                    if y != min(self.times.values())
                    and x != self.curr_player
                ]
            )
        else:
            return random.choice(unattempted)

    def _max_hiding_time_reached(self):
        # TODO: Let frontend know
        # TODO: Add condition on player until location is shared
        # TODO: Work out how to do this
        pass

    def get_times(self) -> dict[str, int]:
        """
        Gets times for the end of the game

        :param self: self
        :return: A dictionary of player names to their hiding times in seconds. Only contains
            players who have actually hidden.
        :rtype: dict[str, int]
        """
        return self.times
