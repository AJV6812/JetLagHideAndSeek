# This is the main file for managing the hide and seek game state. This code is not aware of       
# Discord at all and so could be dropped into any system for running Jet Lag whether virtual or
# real. However this code is completely responsible for knowing everything important (other than
# the player's actual locations) about the game and enforcing as many of the rules as possible. The
# rules that are enforced by the system are below.

from abc import ABC, abstractmethod

# This is an abstract card that represents a card. Each card type will have its own implementation.
class Card(ABC):
    pass

# This is a class to keep track of questions that the seekers have asked and curses.
class InvestigationBook():
    pass

# This is a class to keep track of which cards are in the discard, which cards are in the hand and
# which can still be drawn.
class HiderDeck():
    pass

# This is the main game state interface that the frontend will interact with.
class GameState():
    pass
