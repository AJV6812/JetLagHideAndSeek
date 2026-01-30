import configparser
import random
from hide_and_seek_lite_interfaces import Card
import hide_and_seek_lite_cards as cards

par = configparser.ConfigParser()
par.read("hide_and_seek.cfg")

DEFAULT_MAX_HAND_SIZE = par.getint("MASTER", "DEFAULT_MAX_HAND_SIZE")

class HiderDeck:
    """
    This is a class to keep track of which cards are in the discard, which cards are in the hand
    and which can still be drawn.
    """

    def __init__(self):
        self.hand: list[Card] = []
        self.deck: list[Card] = []
        self.cards: list[Card] = []

        self.max_hand_size = DEFAULT_MAX_HAND_SIZE

        starting_deck: list[tuple[Card, int]] = [
            (
                cards.TimeBonus(
                    3,
                ),
                25,
            ),
            (
                cards.TimeBonus(
                    6,
                ),
                15,
            ),
            (
                cards.TimeBonus(
                    9,
                ),
                10,
            ),
            (
                cards.TimeBonus(
                    12,
                ),
                3,
            ),
            (
                cards.TimeBonus(
                    18,
                ),
                2,
            ),
            (cards.Randomise(), 4),
            (cards.Veto(), 4),
            (cards.Duplicate(), 2),
            (
                cards.DiscardDraw(
                    1,
                    2,
                ),
                4,
            ),
            (
                cards.DiscardDraw(
                    2,
                    3,
                ),
                4,
            ),
            (
                cards.DrawExpand(
                    1,
                    1,
                ),
                2,
            ),
            (cards.Zoologist(), 1),
            (cards.UnguidedTourist(), 1),
            (cards.EndlessTumble(), 1),
            (cards.Hangman(), 1),
            (cards.Chalice(), 1),
            (cards.MediocreTravelAgent(), 1),
            (cards.LuxuryCar(), 1),
            (cards.UTurn(), 1),
            (cards.BridgeTroll(), 1),
            (cards.Water(), 1),
            (cards.JammedDoor(), 1),
            (cards.Cairn(), 1),
            (cards.UrbanExplorer(), 1),
            (cards.DistantCuisine(), 1),
            (cards.RightTurn(), 1),
            (cards.Labyrinth(), 1),
            (cards.BirdGuide(), 1),
            (cards.DrainedBrain(), 1),
            (cards.Ransom(), 1),
            (cards.GamblersFeet(), 1),
            (cards.ProsperousHome(), 1),
            (cards.Void(), 1),
            (cards.ExpressTrain(), 1),
            (cards.ZippedLip(), 1),
            (cards.PlaguedWord(), 1),
            (cards.Queue(), 1),
            (cards.Rewind(), 1),
            (cards.TinyHome(), 1)
        ]

        for card, num in starting_deck:
            for i in range(num):
                self.deck.append(card)
                self.cards.append(card)
        self.discard_pile: list[Card] = []

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

    def play(self, card: Card):
        """
        Called when the hider plays a card. Throws CardNotPlayable if the card cannot be played,
        or is not in the hider's hand. Returns whether the seekers should be informed or not.

        :param card: Card to play
        :type card: Card
        """

        self.hand.remove(card)

        self.discard_pile.append(card)


    def discard(self, card: Card):
        """
        Called when the hider discards a card

        :param card: Card to discard
        :type card: Card
        """
        self.hand.remove(card)
        self.discard_pile.append(card)

    def draw(self):
        """
        Draws a card and adds it to the hider's hand
        """
        self.hand.append(self.deck.pop(random.randint(0, len(self.deck) - 1)))

    def is_legal_hand(self):
        """
        Checks that the hider's hand is within the legal hand size
        """
        return len(self.hand) <= self.max_hand_size
    
    def pop_deck(self) -> Card:
        return self.deck.pop(random.randint(0, len(self.deck) - 1))
    
    def fetch_card_by_name(self, card_name: str)->Card:
        options = [x for x in self.cards if x.get_card_name() == card_name]
        assert len(options) > 0
        return options[0]

