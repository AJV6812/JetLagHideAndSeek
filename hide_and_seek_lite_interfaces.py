"""
This file is for any custom interfaces that have to exist.
"""

from abc import ABC, abstractmethod
import configparser
import datetime

import disnake

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

    def __init__(self):
        pass

    def get_time_bonus(self) -> int:
        """
        Gets number of seconds of time bonuses
        """
        return 0

    @abstractmethod
    def get_inform_seekers(self) -> bool:
        pass

    @abstractmethod
    def get_card_name(self) -> str:
        """
        Returns the card's display name
        """
    
    @abstractmethod
    def get_colour(self)->disnake.Colour:
        pass

    def to_embed(self) -> disnake.Embed:
        embed = disnake.Embed(
            title=self.get_card_name(),
            timestamp=datetime.datetime.now(),
            colour=self.get_colour(),
        )

        embed.set_thumbnail(
            url="https://static.wikia.nocookie.net/jetlag/images/f/f9/JetLagTheIcon.png/revision/latest/scale-to-width-down/250?cb=20240328185702"
        )

        embed.set_footer(text="See rules for further clarification.")

        return embed


class Curse(Card):
    """
    This is an abstract class that represents all hider curse cards.
    """

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

    def get_inform_seekers(self) -> bool:
        return True

    def to_embed(self) -> disnake.Embed:
        embed = disnake.Embed(
            title=self.get_card_name(),
            timestamp=datetime.datetime.now(),
            colour=self.get_colour()
        )

        embed.add_field(
            name="Effect", value=self.get_effect_description(), inline=False
        )
        embed.add_field(
            name="Casting Cost", value=self.get_cost_description(), inline=False
        )
        embed.set_thumbnail(
            url="https://static.wikia.nocookie.net/jetlag/images/f/f9/JetLagTheIcon.png/revision/latest/scale-to-width-down/250?cb=20240328185702"
        )

        embed.set_footer(text="See rules for further clarification.")

        return embed
    
    def get_colour(self) -> disnake.Colour:
        return disnake.Colour.purple()


class Powerup(Card):
    """
    This is an abstract class that represents all powerup cards.
    """

    def get_colour(self) -> disnake.Colour:
        return disnake.Colour.blue()
