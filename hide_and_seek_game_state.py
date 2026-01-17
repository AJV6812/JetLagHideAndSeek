# This is the main file for managing the hide and seek game state. This code is not aware of       
# Discord at all and so could be dropped into any system for running Jet Lag whether virtual or
# real. However this code is completely responsible for knowing everything important (other than
# the player's actual locations) about the game and enforcing as many of the rules as possible. The
# rules that are enforced by the system are below.

import time
import enum
from abc import ABC, abstractmethod
from task_scheduler import TaskScheduler
import hide_and_seek_frontend as frontend
from hide_and_seek_conditions import Condition, ConditionManager

scheduler = TaskScheduler()

# This is an abstract card that represents a card. Each card type will have its own implementation.
class Card(ABC):
    pass

class Question(ABC):
    @abstractmethod
    def getAllocatedTime(self) -> int:
        pass

# This is a class to keep track of questions that the seekers have asked and curses.
class InvestigationBook():
    pass

# This is a class to keep track of which cards are in the discard, which cards are in the hand and
# which can still be drawn.
class HiderDeck():
    pass

class State(enum.Enum):
    INACTIVE=1
    HIDERPHASE=2
    SEEKERPHASE=3
    HIDERDELAY=4

# This is the main game state interface that the frontend will interact with.
class GameState():
    def __init__(self, start_time: int, starting_player: str):
        self.state = State.INACTIVE
        self.start_time = start_time
        self.curr_player = starting_player
        self.investigation = InvestigationBook()
        self.hider_deck = HiderDeck()
        self.conditions = ConditionManager()
        self.times: dict[str, int] = {}
        self.hide_time_start = 0
        self.delay_start = 0
        scheduler.add_function(start_time, self.start_round)

    def start_round(self):
        self.state = State.HIDERPHASE
        self.investigation_book = InvestigationBook()
        self.hider_deck = HiderDeck()
        self.conditions = ConditionManager()
        scheduler.add_function(time.time() + HIDINGTIME, self.release_seekers)
        frontend.start_round()
        

    def release_seekers(self):
        self.state = State.SEEKERPHASE
        self.hide_time_start = time.time()
        frontend.release_seekers()

    def ask_question(self, question: Question):
        if self.conditions.has_condition(Condition.ACTIVEQUESTION):
            raise some custom exception
        scheduler.add_function(int(time.time() + question.getAllocatedTime()), lambda: self.check_question_answered(question, self.investigation_book.get_times_answered(question) + 1))
        self.conditions.add_condition(Condition.ACTIVEQUESTION)
        frontend.ask_question(question, int(time.time() + question.getAllocatedTime()))

    def check_question_answered(self, question:Question, times_answered: int):
        if self.investigation_book.get_times_answered(question) != times_answered:
            self.state = State.HIDERDELAY
            self.investigation_book.reward_mult(0,1)
            self.delay_start = time.time()
            frontend.hider_delay()
    
    def answered_question(self, answer: str):
        frontend.send_answer(answer)
            


        

