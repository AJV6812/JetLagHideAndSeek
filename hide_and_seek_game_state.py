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

import hide_and_seek_cards as cards
from task_scheduler import TaskScheduler
from hide_and_seek_conditions import Condition, ConditionManager
from hide_and_seek_exceptions import (
    CardNotPlayableException,
    QuestionActiveException,
    HandSizeExceededException,
)
from hide_and_seek_interfaces import Question, Card, QuestionInstance
from hide_and_seek_interfaces import Frontend

par = configparser.ConfigParser()
par.read("hide_and_seek.cfg")

HIDING_TIME = par.getint("MASTER", "HIDING_TIME")
PLANNING_TIME = par.getint("MASTER", "PLANNING_TIME")
MAX_SEEKING_TIME = par.getint("MASTER", "MAX_SEEKING_TIME")
DEFAULT_MAX_HAND_SIZE = par.getint("MASTER", "DEFAULT_MAX_HAND_SIZE")


class HiderDeck:
    """
    This is a class to keep track of which cards are in the discard, which cards are in the hand
    and which can still be drawn.
    """

    def __init__(self, game_state, frontend: Frontend):
        self.hand: list[Card] = []
        self.deck: list[Card] = []

        self.max_hand_size = DEFAULT_MAX_HAND_SIZE

        starting_deck: list[tuple[Card, int]] = [
            (cards.TimeBonus(3, game_state), 25),
            (cards.TimeBonus(6, game_state), 15),
            (cards.TimeBonus(9, game_state), 10),
            (cards.TimeBonus(12, game_state), 3),
            (cards.TimeBonus(18, game_state), 2),
            (cards.Randomise(game_state), 4),
            (cards.Veto(game_state), 4),
            (cards.Duplicate(game_state), 2),
            (cards.DiscardDraw(1, 2, game_state), 4),
            (cards.DiscardDraw(2, 3, game_state), 4),
            (cards.DrawExpand(1, 1, game_state), 2),
            (cards.Zoologist(game_state), 1),
            (cards.UnguidedTourist(game_state), 1),
            (cards.EndlessTumble(game_state), 1),
            (cards.Hangman(game_state), 1),
            (cards.Chalice(game_state), 1),
            (cards.MediocreTravelAgent(game_state), 1),
            (cards.LuxuryCar(game_state), 1),
            (cards.UTurn(game_state), 1),
            (cards.BridgeTroll(game_state), 1),
            (cards.Water(game_state), 1),
            (cards.JammedDoor(game_state), 1),
            (cards.Cairn(game_state), 1),
            (cards.UrbanExplorer(game_state), 1),
            (cards.DistantCuisine(game_state), 1),
            (cards.RightTurn(game_state), 1),
            (cards.Labyrinth(game_state), 1),
            (cards.BirdGuide(game_state), 1),
            (cards.DrainedBrain(game_state), 1),
            (cards.Ransom(game_state), 1),
            (cards.GamblersFeet(game_state), 1),
            (cards.ProsperousHome(game_state), 1),
            (cards.Void(game_state), 1),
            (cards.ExpressTrain(game_state), 1),
            (cards.ZippedLip(game_state), 1),
            (cards.PlaguedWord(game_state), 1),
        ]

        for card, num in starting_deck:
            for i in range(num):
                self.deck.append(card)
        self.discard_pile: list[Card] = []
        self.frontend = frontend

    def count_time_bonuses(self) -> int:
        """
        Calculates the time bonus in the hider's hand

        :param self: This object
        :return: The number of seconds of time bonuses granted
        :rtype: int
        """
        return sum([x.get_time_bonus() for x in self.hand])

    def get_hand_size(self) -> int:
        """
        Gets number of cards in hand
        """
        return len(self.hand)

    async def reward(self, draw_num: int, keep_num: int):
        """
        Function that handles the hider drawing x cards and keeping y of them
        """
        if len(self.deck) <= draw_num:
            while len(self.discard_pile) > 0:
                self.deck.append(self.discard_pile.pop(0))
        draw = [
            self.deck.pop(random.randint(0, len(self.deck) - 1))
            for x in range(draw_num)
        ]

        keeping: set[Card] = await self.frontend.select_cards(draw, keep_num, "keep")
        assert len(keeping) <= keep_num

        for i in range(draw_num):
            if i in keeping:
                self.hand.append(draw[i])
            else:
                self.discard_pile.append(draw[i])

    async def play(self, card: Card):
        """
        Called when the hider plays a card. Throws CardNotPlayable if the card cannot be played,
        or is not in the hider's hand.

        :param card: Card to play
        :type card: Card
        """

        if not card in self.hand:
            raise CardNotPlayableException()

        await card.play()
        self.hand.remove(card)

        self.discard_pile.append(card)

        if not self.is_legal_hand() and not card.game_state.conditions.has_condition(
            Condition.HAND_LOCK
        ):
            card.game_state.conditions.add_condition(Condition.HAND_LOCK)

    def discard(self, card: Card):
        """
        Called when the hider discards a card

        :param card: Card to discard
        :type card: Card
        """
        self.hand.remove(card)
        card.discard()
        self.discard_pile.append(card)

    async def draw(self):
        """
        Draws a card and adds it to the hider's hand
        """
        self.hand.append(self.deck.pop(random.randint(0, len(self.deck) - 1)))

    async def is_legal_hand(self):
        """
        Checks that the hider's hand is within the legal hand size
        """
        return len(self.hand) <= self.max_hand_size


class InvestigationBook:
    """
    This is a class to keep track of questions that the seekers have asked.
    """

    def __init__(self):
        self.current_question = None
        self.times_answered: dict[Question, int] = {}
        self.rewards: list[int] = []

    def get_times_answered(self, question: Question) -> int:
        """
        Gets the number of times a question has been answered by the hider this round

        :param self: Description
        :param question: Which question to ask about.
        :type question: Question
        :return: Number of times the question has been asked.
        :rtype: int
        """
        return self.times_answered.get(question, 0)

    def set_current_question(self, question: QuestionInstance):
        """
        Sets the question that the hider is currently being asked.
        Assumes that the seekers are currently asking a question.

        :param question: Question that was just asked
        :type question: QuestionInstance
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
        for i in range(num_questions):
            if i >= len(self.rewards):
                self.rewards.append(multiplier)
            else:
                self.rewards *= multiplier

    async def question_answered(self, hider_deck: HiderDeck):
        """
        Called whenever a question is asked to handle the seeker receiving rewards

        :param hider_deck: The current hider deck
        :type hider_deck: HiderDeck
        """

        assert self.current_question is not None

        self.times_answered[self.current_question] += self.get_times_answered(
            self.current_question
        )

        if len(self.rewards) > 0:
            mult = self.rewards.pop(0)
        else:
            mult = 1

        for number in range(self.times_answered[self.current_question] * mult):
            await hider_deck.reward(*self.current_question.get_reward())
        self.current_question = None


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

    def __init__(
        self,
        start_time: int,
        players: list[str],
        frontend: Frontend,
        scheduler: TaskScheduler,
    ):
        self.state = State.INACTIVE
        self.start_time = start_time
        self.players = players
        self.curr_player = ""
        self.investigation_book = InvestigationBook()
        self.hider_deck = HiderDeck(self, frontend)
        self.conditions = ConditionManager()
        self.times: dict[str, int] = {}
        self.hide_time_start: int = 0
        self.delay_start: int = 0
        self.hider_time_bonus: int = 0
        self.scheduler = scheduler
        scheduler.add_task(start_time, self.start_round())
        self.next_player = self._get_next_player()
        self.frontend = frontend

        scheduler.add_task(
            int(time.time()) + 1, frontend.announce_next_player(self.next_player)
        )

    async def start_round(self):
        """
        Converts the game state from inactive to the hiding phase. Resets the investigation book,
        hider deck, condition system, current player name, and sets the scheduler to start the
        seeking phase in due course.
        """
        if self.state == State.INACTIVE:
            self.scheduler.remove_task(self.start_round())
            self.state = State.HIDERPHASE
            self.investigation_book = InvestigationBook()
            self.hider_deck = HiderDeck(self, self.frontend)
            self.conditions = ConditionManager()
            self.curr_player = self.next_player
            self.scheduler.add_task(
                int(time.time() + HIDING_TIME), self._release_seekers()
            )
            self.scheduler.add_task(
                int(time.time()),
                self.frontend.announce_round_start(int(time.time() + HIDING_TIME)),
            )

    async def _release_seekers(self):
        """
        Function is called when the hiding time is up and the seekers are released.
        The frontend is called to let both the seekers and hider know.
        """
        self.state = State.SEEKERPHASE
        self.hide_time_start = int(time.time())
        self.scheduler.add_task(
            int(time.time() + MAX_SEEKING_TIME), self._max_hiding_time_reached()
        )
        self.hider_time_bonus = 0
        await self.frontend.announce_seekers_released()

    async def ask_question(self, question: QuestionInstance):
        """
        Called when the hiders ask a specific question. Can raise QuestionActiveException, if
        there is already a question been asked. If valid, the frontend is called so the hider can
        be informed.

        :param question: Question that is being asked, assumed to not be a thermometer
        :type question: QuestionInstance
        """

        # TODO: But what if not a thermometer

        if self.conditions.has_condition(Condition.ACTIVEQUESTION):
            raise QuestionActiveException()
        self.scheduler.add_task(
            int(time.time() + question.get_allocated_time()),
            self._check_question_answered(
                question, self.investigation_book.get_times_answered(question) + 1
            ),
        )
        self.conditions.add_condition(Condition.ACTIVEQUESTION)
        await self.frontend.pose_question(question)

    async def _check_question_answered(self, question: QuestionInstance, times_answered: int):
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
            await self.frontend.question_time_expired()

    async def answered_question(self, answer: str):
        """
        Called when a question is answered. Raises HandSizeExceeded if the hider's hand size is
        too large and therefore cannot answer the question.

        :param answer: The hider's given answer
        :type answer: str
        """

        if self.conditions.has_condition(Condition.HAND_LOCK):
            raise HandSizeExceededException()

        self.conditions.remove_condition(Condition.ACTIVEQUESTION)
        penalty = None
        if self.state == State.HIDERDELAY:
            self.state = State.SEEKERPHASE
            penalty = int(time.time() - self.delay_start)
            self.hider_time_bonus -= penalty
        
        assert self.investigation_book.current_question is not None

        await self.frontend.reveal_answer(self.investigation_book.current_question, answer, penalty)

        self.conditions.add_condition(Condition.HAND_LOCK)
        await self.investigation_book.question_answered(self.hider_deck)
        if self.hider_deck.is_legal_hand():
            self.conditions.remove_condition(Condition.HAND_LOCK)

    async def hider_caught(self):
        """
        Called when the hider is caught. Tallies the hider's time, and sets the next player.
        """
        self.state = State.INACTIVE
        self.hider_time_bonus += self.hider_deck.count_time_bonuses()
        self.times[self.curr_player] = max(
            (int(time.time()) - self.hide_time_start + self.hider_time_bonus),
            self.times.get(self.curr_player, 0),
        )
        self.next_player = self._get_next_player()
        self.scheduler.remove_task(self._max_hiding_time_reached())
        self.scheduler.add_task(int(time.time() + PLANNING_TIME), self.start_round())
        await self.frontend.announce_next_player(
            self.next_player,
            (int(time.time()) - self.hide_time_start + self.hider_time_bonus),
        )

    async def play_card(self, card: Card):
        await self.hider_deck.play(card)

    def _get_next_player(self) -> str:
        unattempted = [x for x in self.players if x not in self.times]
        if len(unattempted) == 0:
            return random.choice(
                [
                    x
                    for x, y in self.times.items()
                    if y != min(self.times.values()) and x != self.curr_player
                ]
            )
        else:
            return random.choice(unattempted)

    async def _max_hiding_time_reached(self):
        await self.frontend.announce_seeking_time_expired()
        # TODO: Add condition on player until location is shared
        # TODO: Work out how to do this

    def get_times(self) -> dict[str, int]:
        """
        Gets times for the end of the game

        :param self: self
        :return: A dictionary of player names to their hiding times in seconds. Only contains
            players who have actually hidden.
        :rtype: dict[str, int]
        """
        return self.times
