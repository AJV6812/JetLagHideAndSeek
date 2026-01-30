import random
from dataclasses import dataclass
import os
import configparser

import disnake
from disnake.ext import commands
from dotenv import load_dotenv

from hide_and_seek_lite_deck import HiderDeck
from hide_and_seek_lite_interfaces import Curse

config = configparser.ConfigParser()
config.read("hide_and_seek.cfg")

load_dotenv()
TOKEN = os.getenv("TOKEN")

client = commands.InteractionBot()


async def autocomp_hider_hand(
    inter: disnake.ApplicationCommandInteraction, user_input: str
):
    return [
        x.get_card_name()
        for x in clientData.hider_deck.hand
        if user_input.lower() in x.get_card_name().lower()
    ]

async def autocomp_all_cards(
    inter: disnake.ApplicationCommandInteraction, user_input: str
):
    return sorted(set([
        x.get_card_name()
        for x in clientData.hider_deck.cards
        if user_input.lower() in x.get_card_name().lower()
    ]))[:25]

@dataclass
class ClientData:
    hider_channel: int
    seeker_channel: int
    hider_deck: HiderDeck


clientData = ClientData(845462051464019998, 560022746973601792, HiderDeck())


async def fetch_hider_channel() -> disnake.DMChannel:
    return await client.create_dm(await client.fetch_user(clientData.hider_channel))


async def fetch_seeker_channel() -> disnake.DMChannel:
    return await client.create_dm(await client.fetch_user(clientData.seeker_channel))

async def check_hider(ctx: disnake.ApplicationCommandInteraction):
    if ctx.author.id != clientData.hider_channel:
        await ctx.response.send_message("No permission to use this command.")
        return False
    return True

# Command to display hand
@client.slash_command(description="Displays your hand.")
async def display_hand(ctx: disnake.ApplicationCommandInteraction):
    if not await check_hider(ctx):
        return
    if len(clientData.hider_deck.hand) == 0:
        await ctx.response.send_message("Hand is empty.")
        return
    elif len(clientData.hider_deck.hand) >= 10:
        await ctx.response.send_message("Hand is too full.")
        return
    await ctx.response.send_message(
        "Your hand is below.", embeds=[x.to_embed() for x in clientData.hider_deck.hand]
    )
    if not clientData.hider_deck.is_legal_hand():
        await ctx.followup.send("WARNING: OVER DEFAULT HAND SIZE LIMIT OF 6")


async def secondary_display_hand(ctx: disnake.ApplicationCommandInteraction):
    if not await check_hider(ctx):
        return
    await ctx.followup.send(
        "Your hand is below.", embeds=[x.to_embed() for x in clientData.hider_deck.hand]
    )
    if not clientData.hider_deck.is_legal_hand():
        await ctx.followup.send("WARNING: OVER DEFAULT HAND SIZE LIMIT OF 6")


# Command to draw a card
@client.slash_command(description="Draws a random card from the deck.")
async def draw(ctx: disnake.ApplicationCommandInteraction):
    if not await check_hider(ctx):
        return
    clientData.hider_deck.draw()
    await display_hand(ctx)


# Command to select x from y
@client.slash_command(description="Handles reward from asking a question. By default you choose one card from the result.")
async def reward(
    ctx: disnake.ApplicationCommandInteraction, draw_number: int, select_number: int = 1
):
    if not await check_hider(ctx):
        return
    cards = [clientData.hider_deck.pop_deck() for x in range(draw_number)]

    view = disnake.ui.View(timeout=240)

    async def card_callback(inter: disnake.MessageInteraction):
        view.stop()

    item = disnake.ui.StringSelect(
        placeholder="Click to choose cards:",
        min_values=select_number,
        max_values=select_number,
        options=[
            disnake.SelectOption(label=y.get_card_name(), value=str(x))
            for x, y in enumerate(cards)
        ],
    )
    item.callback = card_callback

    view.add_item(item)

    await ctx.response.send_message(f"Select {select_number} card(s).", view=view)
    if len([x.to_embed() for x in cards if isinstance(x, Curse)]) != 0:
        await ctx.followup.send(
            embeds=[x.to_embed() for x in cards if isinstance(x, Curse)]
        )

    if not await view.wait():
        for card in [cards[int(x)] for x in item.values]:
            clientData.hider_deck.hand.append(card)
        await secondary_display_hand(ctx)
    else:
        await ctx.followup.send("Timed out.")


# Command to play card
@client.slash_command(description="Plays a card and notifies the hiders if appropriate. Additional effects handled manually.")
async def play(
    ctx: disnake.ApplicationCommandInteraction,
    card_name: str = commands.Param(autocomplete=autocomp_hider_hand),
):
    if not await check_hider(ctx):
        return
    card = clientData.hider_deck.fetch_card_by_name(card_name)
    clientData.hider_deck.play(card)

    if card.get_inform_seekers():
        await (await fetch_seeker_channel()).send(
            "Hider has played this card.", embed=card.to_embed()
        )

    await ctx.response.send_message("Card played successfully.", embed=card.to_embed())
    await secondary_display_hand(ctx)


# Command to discard card
@client.slash_command(description="Discards a card from your hand.")
async def discard(
    ctx: disnake.ApplicationCommandInteraction,
    card_name: str = commands.Param(autocomplete=autocomp_hider_hand),
):
    if not await check_hider(ctx):
        return
    card = clientData.hider_deck.fetch_card_by_name(card_name)
    clientData.hider_deck.discard(card)

    await ctx.response.send_message("Card discarded successfully.")
    await secondary_display_hand(ctx)


@client.slash_command(description="Forcibly gives a copy of any card. Do not abuse.")
async def give_card(
    ctx: disnake.ApplicationCommandInteraction,
    card_name: str = commands.Param(autocomplete=autocomp_all_cards),
):
    if not await check_hider(ctx):
        return
    card = clientData.hider_deck.fetch_card_by_name(card_name)
    clientData.hider_deck.hand.append(card)
    clientData.hider_deck.deck = [x for x in clientData.hider_deck.deck if x != card]
    await display_hand(ctx)


# Roll xdy
@client.slash_command(description="Rolls any number of dice with any number of sides. By default rolls a single 6 sided die.")
async def roll(
    ctx: disnake.ApplicationCommandInteraction, sides: int = 6, number: int = 1
):
    if number <= 1:
        await ctx.response.send_message(f"Result is: **{random.randint(1,sides)}**")
    else:
        res = [random.randint(1, sides) for x in range(number)]
        await ctx.response.send_message(
            f"Result is: **{sum(res)}**\n[{', '. join([str(x) for x in res])}]"
        )


# Reset hider deck
@client.slash_command(description="Don't touch")
async def reset(ctx: disnake.ApplicationCommandInteraction):
    clientData.hider_deck = HiderDeck()


@client.slash_command(description="Don't touch")
async def change_discord_users(
    ctx: disnake.ApplicationCommandInteraction, hider_id: str, seeker_id: str
):
    await ctx.response.defer()
    clientData.hider_channel = int(hider_id)
    clientData.seeker_channel = int(seeker_id)
    await (await fetch_hider_channel()).send("Testing!")
    await (await fetch_seeker_channel()).send("Testing!")
    await ctx.followup.send("All working.")


@client.event
async def on_ready():
    pass


client.run(TOKEN)
