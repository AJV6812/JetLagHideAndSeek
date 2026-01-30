from disnake.colour import Colour
import hide_and_seek_lite_interfaces as interfaces

class TimeBonus(interfaces.Card):
    """
    Class for abstract time bonus cards
    """
    def __init__(self, time_bonus_minute: int):
        super().__init__()
        self.time_bonus_minute = time_bonus_minute

    def get_time_bonus(self) -> int:
        return self.time_bonus_minute * 60

    def get_card_name(self) -> str:
        return f"{self.time_bonus_minute} Minute Time Bonus"
    
    def get_inform_seekers(self) -> bool:
        return False
    
    def get_colour(self) -> Colour:
        return Colour.red()


class Randomise(interfaces.Powerup):
    def get_card_name(self) -> str:
        return "Randomise Question"
    
    def get_inform_seekers(self) -> bool:
        return True


class Veto(interfaces.Powerup):
    def get_card_name(self) -> str:
        return "Veto Question"

    def get_inform_seekers(self) -> bool:
        return True


class Duplicate(interfaces.Powerup):
    def get_card_name(self) -> str:
        return "Duplicate Card"

    def get_inform_seekers(self) -> bool:
        return False


class DiscardDraw(interfaces.Powerup):
    def __init__(
        self,
        discard_amount: int,
        draw_amount: int,
    ):
        self.draw_amount = draw_amount
        self.discard_amount = discard_amount

    def get_card_name(self) -> str:
        return f"Discard {self.discard_amount}, Draw {self.draw_amount}"

    def get_inform_seekers(self) -> bool:
        return False


class DrawExpand(interfaces.Powerup):
    def __init__(
        self,
        draw_amount: int,
        expand_amount: int,
    ):
        self.draw_amount = draw_amount
        self.expand_amount = expand_amount

    def get_card_name(self) -> str:
        return f"Draw {self.draw_amount}, Expand Max Hand Size by {self.expand_amount}"
    
    def get_inform_seekers(self) -> bool:
        return False


class Zoologist(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Zoologist"

    def get_effect_description(self) -> str:
        return "Take a photo of a wild fish, bird, mammal, reptile, amphibian or bug. The seeker(s) must take a picture of a wild animal in the same category before asking another question."

    def get_cost_description(self) -> str:
        return "A photo of an animal"


class UnguidedTourist(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Unguided Tourist"

    def get_effect_description(self) -> str:
        return "Send the seeker(s) an unzoomed google Street View image from a street within 150m of where they are now. The shot has to be parallel to the horizon and include at least one human-built structure other than a road. Without using the internet for research, they must find what you sent them in real life before they can use transportation or ask another question. They must send a picture the hiders for verification."

    def get_cost_description(self) -> str:
        return "Seeker(s) must be outside"


class EndlessTumble(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Endless Tumble"

    def get_effect_description(self) -> str:
        return "Seekers Must roll a die at least 30m and have it land on a 5 or a 6 before they can ask another question. The die must roll the full distance, unaided, using only the momentum from the initial throw and gravity to travel the 100ft (30m). If the seekers accidentally hit someone with a die you are awarded a M20 minute bonus"

    def get_cost_description(self) -> str:
        return "Roll a die. If its 5 or 6 this card has no effect."


class Hangman(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Hidden Hangman"

    def get_effect_description(self) -> str:
        return "Before asking another question or boarding another form of transportation, seeker(s) must be the hider(s) in game of hangman."

    def get_cost_description(self) -> str:
        return "Discard 2 cards"


class Chalice(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Overflowing Chalice"

    def get_effect_description(self) -> str:
        return "For the next three questions, you may draw (not keep) an additional card when drawing from the hider deck"

    def get_cost_description(self) -> str:
        return "Discard a card"


class MediocreTravelAgent(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Mediocre Travel Agent"

    def get_effect_description(self) -> str:
        return "Choose any publicly-accessible place within 400m of the seeker(s) current location. They cannot currently be on transit. They must go there, and spend at least M5 minutes there, before asking another question. They must send you at least three photos of them enjoying their vacation, and procure an object to bring you as souvenir. If this souvenir is lost before they can get to you, you are awarded and extra 45 minutes."

    def get_cost_description(self) -> str:
        return "Seekers must not currently be on transit."


class LuxuryCar(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Luxury Car"

    def get_effect_description(self) -> str:
        return "Take a photo of a car. The seekers must take a photo of a more expensive car before asking another question."

    def get_cost_description(self) -> str:
        return "A photo of a car"


class UTurn(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the U-Turn"

    def get_effect_description(self) -> str:
        return "Seeker(s) must disembark their current mode of transportation at the next station (as long as that station is served by another form of transit in the next [S0.5, M0.5, L1] hours"

    def get_cost_description(self) -> str:
        return "Seekers must be heading the wrong way. (Their next station is further from you then they are.)"


class BridgeTroll(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Bridge Troll"

    def get_effect_description(self) -> str:
        return "The seekers must ask their next question from under a bridge"

    def get_cost_description(self) -> str:
        return "Seekers must be at least 1.5km from you"


class Water(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Water Weight"

    def get_effect_description(self) -> str:
        return "Seeker(s) must acquire and carry at least 2 liters of liquid per seeker for the rest of your run. They cannot ask another question until they have acquired the liquid. The water may be distributed between seeker as they see fit. If the liquid is lost or abandoned at any point the hider is awarded a 30 minute bonus"

    def get_cost_description(self) -> str:
        return "Seekers must be within 300 meters of a body of water"

class JammedDoor(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Jammed Door"

    def get_effect_description(self) -> str:
        return "For the next 1 hour, whenever the seeker(s) want to pass through a doorway into a building, business, train, or other vehicle they must first roll 2 dice. If they do not roll a 7 or higher they cannot enter that space (including through other doorways) any given doorway can be reattempted after 10 minutes."

    def get_cost_description(self) -> str:
        return "Discard 2 cards"


class Cairn(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Cairn"

    def get_effect_description(self) -> str:
        return "You have one attempt to stack as many rocks on top of each other as you can in a freestanding tower. Each rock may only touch one other rock. Once you have added a rock to the tower it may not be removed. Before adding another rock, the tower must stand for at least 5 seconds. If at any point any rock other then the base rock touches the ground, your tower has fallen. Once your tower falls tell the seekers how many rocks high your tower was when it last stood for five seconds. The seekers must then construct a rock tower of the same number of rucks, under the same parameters before asking another question. If their tower falls they must restart. The rocks must be found in nature and both teams must disperse the rocks after building."

    def get_cost_description(self) -> str:
        return "Build a rock tower"


class UrbanExplorer(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Urban Explorer"

    def get_effect_description(self) -> str:
        return "For the rest of the run seekers cannot ask question when they are on transit or in a train station"

    def get_cost_description(self) -> str:
        return "Discard 2 cards"


class DistantCuisine(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Distant Cuisine"

    def get_effect_description(self) -> str:
        return "Find a restaurant within your zone that explicitly serves food from a specific foreign country. The seekers must visit a restaurant serving food from a country that is equal or great distance away before asking another question"

    def get_cost_description(self) -> str:
        return "You must be at the restaurant"


class RightTurn(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Right Turn"

    def get_effect_description(self) -> str:
        return "For the next 40 minutes the seekers can only turn right at any street intersection. If at any point they find themselves in dead end where they cannot continue forward or turn right for another 300m they must do a full 180. A right turn is defined as a road at any angle that veers to the right of the seekers"

    def get_cost_description(self) -> str:
        return "Discard a card"


class Labyrinth(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Labyrinth"

    def get_effect_description(self) -> str:
        return "Spend up to 20 minutes drawing a solvable maze and send a photo of it to the seekers. You cannot use the internet to research maze designs. The seekers musts solve the maze before asking another question. Only one hider may draw the maze."

    def get_cost_description(self) -> str:
        return "Draw a maze"


class BirdGuide(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Bird Guide"

    def get_effect_description(self) -> str:
        return "You have one chance to film a bird for as long as possible. Up to 10 minutes straight, if at any point the bird leaves the frame your timer is stopped. The seekers must then film a bird for the same amount of time or longer"

    def get_cost_description(self) -> str:
        return "Film a bird"


class DrainedBrain(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Drained Brain"

    def get_effect_description(self) -> str:
        return "Choose three questions in different categories. The seekers cannot ask those questions for the rest of the run."

    def get_cost_description(self) -> str:
        return "Discard your hand"


class Ransom(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Ransom Note"

    def get_effect_description(self) -> str:
        return "The next question that the seekers ask must be composed of words and letters cut out of any printed material. The question must be coherent and include at least 5 words."

    def get_cost_description(self) -> str:
        return "Spell out 'Ransom Note' as a ransom note"


class GamblersFeet(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Gambler's Feet"

    def get_effect_description(self) -> str:
        return "For the next 40 minutes seekers must roll a die before they take any steps in any direction, they may take that many steps before rolling again"

    def get_cost_description(self) -> str:
        return "There is a 1/2 chance this curse is cleared immediately."


class ProsperousHome(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Prosperous Home"

    def get_effect_description(self) -> str:
        return "Expand the radius of your hiding zone by 50%."

    def get_cost_description(self) -> str:
        return "Discard at least 10 minutes worth of bonuses."


class Void(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Void"

    def get_effect_description(self) -> str:
        return "For the next three questions that the seekers ask, there is a 2/3 chance that question is automatically vetoed."

    def get_cost_description(self) -> str:
        return "Discard a veto."


class ExpressTrain(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Express Train"

    def get_effect_description(self) -> str:
        return "Seekers cannot disembark any transit for the next 20 minutes, unless they've reached the end of a line."

    def get_cost_description(self) -> str:
        return "Discard at least 15 minutes worth of time bonuses."


class ZippedLip(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Zipped Lip"

    def get_effect_description(self) -> str:
        return "Seekers can only communicate to one another through gestures and closed-mouth sounds for the next 20 minutes. They can speak to other people but cannot speak or write any message intended or another seeker."

    def get_cost_description(self) -> str:
        return "Discard a power-up."


class PlaguedWord(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Plagued Word"

    def get_effect_description(self) -> str:
        return "For the next hour, asking a question creates a 5km radius where questions cannot be asked until this curse expires."

    def get_cost_description(self) -> str:
        return "Seekers must be at least 25km away from you."

class Queue(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Queue"

    def get_effect_description(self) -> str:
        return "Seekers may not ask another question until they've waited in line for at least five minutes. They may wait in different lines, but they cannot wait in the same line more than once.\nThey may not let people cut in front of them in line, and lines must have at least two people when they enter them."

    def get_cost_description(self) -> str:
        return "You must currently be in line somewhere."

class Rewind(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Rewind"

    def get_effect_description(self) -> str:
        return "You must ask your next question from the exact place you asked your last question."

    def get_cost_description(self) -> str:
        return "The last question must have been asked during the end game."

class TinyHome(interfaces.Curse):
    def get_card_name(self) -> str:
        return "Curse of the Tiny Home"

    def get_effect_description(self) -> str:
        return "All time bonus cards held at the end of this round is worth 50 percent extra."

    def get_cost_description(self) -> str:
        return "The radius of your hiding zone is halved. This curse cannot be played during the endgame."

