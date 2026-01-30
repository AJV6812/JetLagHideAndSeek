"""
This file is for any custom interfaces that have to exist.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
import configparser

if TYPE_CHECKING:
    from hide_and_seek_game_state import GameState

par = configparser.ConfigParser()
par.read("hide_and_seek.cfg")

DEFAULT_ALLOCATED_QUESTION_TIME = par.getint(
    "MASTER", "DEFAULT_ALLOCATED_QUESTION_TIME"
)


class Card(ABC):
    """
    This is an abstract class that represents a card. Each card type will have its own
    implementation.
    """

    def __init__(self, game_state_inst: GameState):
        self.game_state = game_state_inst

    async def play(self):
        """
        Plays a card
        """

    def discard(self):
        """
        Discards a card
        """

    def get_time_bonus(self) -> int:
        """
        Gets number of seconds of time bonuses
        """
        return 0

    def _playable(self) -> bool:
        """
        Returns whether the card is playable
        """
        return True

    def get_game_state(self) -> GameState:
        """
        Returns the game state the card belongs to
        """
        return self.game_state

    @abstractmethod
    def get_card_name(self) -> str:
        """
        Returns the card's display name
        """


class Curse(Card):
    """
    This is an abstract class that represents all hider curse cards.
    """

    @abstractmethod
    async def play(self):
        await self.get_game_state().frontend.announce_curse(self)

    @abstractmethod
    def get_cost_description(self) -> str:
        """
        Gets the display cost of a curse.
        """

    @abstractmethod
    def get_effect_description(self) -> str:
        """
        Gets the display effect of a curse.
        """


class Powerup(Card):
    """
    This is an abstract class that represents all powerup cards.
    """


class Question(ABC):
    """
    This is an abstract class that represents a question. Each question type will implement
    this separately, and each specific question will implement that question type
    """

    @abstractmethod
    def get_short_question(self) -> str:
        """
        :return: One word version of the question that can be used in drop down boxes
        :rtype: str
        """

    @abstractmethod
    def get_full_question(self) -> str:
        """
        :return: Question that can be displayed to the hider
        :rtype: str
        """

    def get_allocated_time(self) -> int:
        """
        Gets the amount of time the hider is allocated to answer this question

        :param self: This object
        :return: The number of seconds to answer
        :rtype: int
        """
        return DEFAULT_ALLOCATED_QUESTION_TIME

    @abstractmethod
    def get_reward(self) -> tuple[int, int]:
        """
        The reward that the hider receives from answering this question

        :return: A tuple containing two numbers, the first is how many cards to draw, and the
            second how many to keep
        :rtype: tuple[int, int]
        """
    
    @abstractmethod
    def to_instance(self, user_input:str) -> QuestionInstance:
        pass

    def __eq__(self, other) -> bool:
        # TODO: Implement
        return str(self) == str(other)


class QuestionInstance(Question):
    @abstractmethod
    def get_user_input(self) -> str:
        """
        This method returns the input that the seekers must provide when asking a question at a specific point in time

        :return: Description
        :rtype: str
        """
    
    @abstractmethod
    def get_options(self) -> list[str]:
        """
        Gets possible answers

        :return: List of strings that represents each option
        :rtype: list[str]
        """


class Frontend(ABC):
    """
    This is the abstract class that represents any frontend.
    """

    @abstractmethod
    async def select_cards(
        self, cards: list[Card], num_select: int, reason: str
    ) -> set[Card]:
        """
        Asks the hider to select which cards to keep from a given list

        :param cards: List of cards the hider can choose from
        :type cards: list[Card]
        :param num_keeping: Number of cards the hider is allowed to keep
        :type num_keeping: int
        :param reason: Reason why the hider is being asked
        :type reason: str
        :return: A set of indices of size num_keeping which represents the hider's choice
        :rtype: set[int]
        """

    @abstractmethod
    async def announce_round_start(self, hiding_time_end: int):
        pass

    @abstractmethod
    async def announce_seekers_released(self):
        pass

    @abstractmethod
    async def pose_question(self, question: QuestionInstance):
        pass

    @abstractmethod
    async def question_time_expired(self):
        pass

    @abstractmethod
    async def reveal_answer(
        self, question: QuestionInstance, answer: str, penalty: int | None = None
    ):
        pass

    @abstractmethod
    async def announce_next_player(
        self, next_player: str, last_result: int | None = None
    ):
        pass

    @abstractmethod
    async def announce_seeking_time_expired(self):
        pass

    @abstractmethod
    async def announce_curse(self, card: Curse):
        pass
