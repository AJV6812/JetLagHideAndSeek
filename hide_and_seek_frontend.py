import asyncio
import time
import os
from dataclasses import dataclass
import configparser

import disnake
from disnake.ext import commands, tasks
from disnake import embeds
from dotenv import load_dotenv

from hide_and_seek_game_state import GameState
from hide_and_seek_interfaces import Card, Curse, Frontend, Question, QuestionInstance
from hide_and_seek_questions import MatchingQuestion
from task_scheduler import TaskScheduler


config = configparser.ConfigParser()
config.read("hide_and_seek.cfg")

load_dotenv()
TOKEN = os.getenv("TOKEN")

client = commands.InteractionBot()


class DiscordFrontend(Frontend):
    async def select_cards(
        self, cards: list[Card], num_select: int, reason: str
    ) -> set[Card]:
        assert client_data.hider_channel is not None

        view = disnake.ui.View(timeout=300)

        async def card_callback(inter: disnake.MessageInteraction):
            view.stop()

        item = disnake.ui.StringSelect(
            placeholder="Click to choose cards:",
            min_values=num_select,
            max_values=num_select,
            options=[
                disnake.SelectOption(label=y.get_card_name(), value=str(x))
                for x, y in enumerate(cards)
            ],
        )
        item.callback = card_callback

        view.add_item(item)

        await client_data.hider_channel.send(
            f"Select {num_select} cards to {reason}.", view=view
        )

        if await view.wait():
            return set([cards[int(x)] for x in item.values])
        else:
            # TODO Implement
            raise NotImplementedError()

    async def announce_round_start(self, hiding_time_end: int):
        assert client_data.hider_channel is not None
        assert client_data.seeker_channel is not None
        await client_data.hider_channel.send(
            f"Round started! Hiding time ends <t:{hiding_time_end}:R>."
        )
        await client_data.seeker_channel.send(
            f"Round started! Hiding time ends <t:{hiding_time_end}:R>."
        )

    async def announce_seekers_released(self):
        assert client_data.hider_channel is not None
        assert client_data.seeker_channel is not None
        await client_data.hider_channel.send(
            "Hiding time over! Seekers are free to move."
        )
        await client_data.seeker_channel.send(
            "Hiding time over! Seekers are free to move."
        )

    async def pose_question(self, question: QuestionInstance):
        assert client_data.hider_channel is not None

        await client_data.hider_channel.send(
            f"Please answer the following question: {question.get_full_question()}. Use /answer to answer."
        )

    async def question_time_expired(self):
        pass  # TODO: Implement

    async def reveal_answer(
        self, question: QuestionInstance, answer: str, penalty: int | None = None
    ):
        assert penalty is None  # TODO: But what if it's not

        assert client_data.seeker_channel is not None

        await client_data.seeker_channel.send(
            f"The answer to {question.get_full_question()} is '{answer}'."
        )

    async def announce_next_player(
        self, next_player: str, last_result: int | None = None
    ):
        assert last_result is None  # TODO: But what if it's not
        assert client_data.hider_channel is not None
        assert client_data.seeker_channel is not None
        await client_data.hider_channel.send(f"The next player will be {next_player}.")
        await client_data.seeker_channel.send(f"The next player will be {next_player}.")

    async def announce_seeking_time_expired(self):
        pass  # TODO: Implement

    async def announce_curse(self, card: Curse):
        pass  # TODO: Implement


# TODO: Call ask_question
# TODO: Call answered_question
# TODO: Call hider_caught
# TODO: Call play_card
# TODO: Call get_times
# TODO: Check all errors are handled

@dataclass
class ClientData:
    hider_channel: disnake.DMChannel | None = None
    seeker_channel: disnake.DMChannel | None = None
    game_state: GameState | None = None
    scheduler: TaskScheduler | None = None


# async def autocomp_order_sets(
#     inter: disnake.ApplicationCommandInteraction, user_input: str
# ):
#     return [
#         x for x in clientData.currentMessages.keys() if user_input.lower() in x.lower()
#     ]


# def formatDollar(value: int | float) -> str:
#     return f"${int(value):,}"


# def formatNumber(num: int | float) -> str:
#     return f"{int(num):,}"


# def formatEmbed(orderSet: ProcessedOrderSet) -> embeds.Embed:
#     secStatus = orderSet.formatSecStatus()
#     if float(secStatus) <= 0:
#         secStatus = "negative"
#     embed = embeds.Embed(
#         title=formatDollar(orderSet.profit),
#         description=orderSet.systemName,
#         color=secColours[secStatus],
#     )

#     primaryOrder = max(orderSet.procMarketOrders)

#     embed.set_thumbnail(url=primaryOrder.icon)
#     embed.add_field(name="Region", value=orderSet.regionName, inline=True)
#     embed.add_field(name="Security", value=orderSet.formatSecStatus(), inline=True)
#     embed.add_field(name="Jumps", value=orderSet.distance, inline=True)
#     embed.add_field(
#         name="% Increase", value=orderSet.formatProfitIncrease(), inline=True
#     )
#     embed.add_field(name="Cost", value=formatDollar(orderSet.costs), inline=True)
#     embed.add_field(
#         name="Speculative", value=formatDollar(orderSet.speculative), inline=True
#     )
#     embed.add_field(
#         name="Volume", value=formatNumber(orderSet.totalVolume), inline=True
#     )

#     return embed


# def similar(
#     newOrderSet: list[ProcessedOrderSet],
#     originalOrderSet: tuple[ProcessedOrderSet, ...] | None,
# ):
#     if originalOrderSet == None:
#         return False

#     assert len(newOrderSet) == len(originalOrderSet) == 10
#     for orderNum in range(10):
#         if (
#             newOrderSet[orderNum].systemName != originalOrderSet[orderNum].systemName
#             or newOrderSet[orderNum].profit - originalOrderSet[orderNum].profit
#             > NOTABLEPROFITINCREASE
#         ):
#             return False

#     return True

# @tasks.loop(minutes=1)
# async def watchKillboard():
#     interestingSystems = set()
#     for order in clientData.currentMessages.values():
#         interestingSystems = interestingSystems.union(order[1].route)

#     killHash = fetchZkillHash()
#     while killHash != "None":
#         mail = fetchKillMail(killHash)
#         if interestingKill(mail, interestingSystems) and clientData.dmchannel is not None:
#             await clientData.dmchannel.send(formattedKillMail(mail))
#         killHash = fetchZkillHash()

# @tasks.loop(minutes=15)
# async def chewContracts():
#     await cacheContractItems(20)


@tasks.loop(seconds=1)
async def update():
    assert client_data.scheduler is not None
    await client_data.scheduler.check_tasks()


# async def clearDMs():
#     assert clientData.dmchannel is not None
#     async for msg in clientData.dmchannel.history(limit=None):
#         if msg.author == client.user:
#             await msg.delete()


@client.event
async def on_ready():
    user = await client.fetch_user(560022746973601792)
    client_data.hider_channel = await user.create_dm()
    client_data.seeker_channel = await (
        await client.fetch_user(852468100503044096)
    ).create_dm()

    print("Connected to Discord")

    client_data.scheduler = TaskScheduler()

    client_data.game_state = GameState(
        int(time.time()) + 5, ["Ben", "Adam"], DiscordFrontend(), client_data.scheduler
    )

    # await client_data.game_state.answered_question("Yes")
    update.start()

    await asyncio.sleep(15)


# def formatTable(
#     headers: list[str], values: list[list[str]], num: list[bool]
# ) -> str:
#     outputstring = ""
#     maxwidths = []
#     for columnno, column in enumerate(headers):
#         maxwidth = len(column)
#         for row in values:
#             if maxwidth < len(row[columnno]):
#                 maxwidth = len(row[columnno])
#         maxwidths.append(maxwidth)
#     # outputstring += ("-"*64+"GUARANTEED "+ordernames[safe]+" ORDERS"+ "-"*(sum(maxwidths)+(len(output)-1)*3-len("-"*64+"GUARANTEED "+ordernames[safe]+" ORDERS")))+"\n"
#     outputstring += (
#         " | ".join([x + " " * (maxwidths[y] - len(x)) for y, x in enumerate(headers)])
#     ) + "\n"
#     outputstring += (
#         " | ".join(["-" * (maxwidths[y]) for y in range(len(headers))])
#     ) + "\n"
#     for value in values[:-1]:
#         outputstring += (
#             " | ".join(
#                 [
#                     (
#                         (x + " " * (maxwidths[y] - len(x)))
#                         if not num[y]
#                         else (" " * (maxwidths[y] - len(x)) + x)
#                     )
#                     for y, x in enumerate(value)
#                 ]
#             )
#         ) + "\n"

#     outputstring += (
#         " | ".join(["-" * (maxwidths[y]) for y in range(len(headers))])
#     ) + "\n"
#     value = values[-1]
#     outputstring += (
#         " | ".join(
#             [
#                 (
#                     (x + " " * (maxwidths[y] - len(x)))
#                     if not num[y]
#                     else (" " * (maxwidths[y] - len(x)) + x)
#                 )
#                 for y, x in enumerate(value)
#             ]
#         )
#     ) + "\n"

#     return outputstring


# def makeTable(orderSet: ProcessedOrderSet) -> str:
#     headers = ["NAME", "PROFIT", "COST", "VOLUME", "SPECULATIVE"]
#     num = [False, True, True, True, True]
#     values: list[list[str]] = []
#     for order in orderSet.procAllOrders:
#         values.append(
#             [
#                 order.getName(),
#                 formatDollar(order.profit),
#                 formatDollar(order.costs),
#                 formatNumber(order.totalVolume),
#                 formatDollar(order.speculative),
#             ]
#         )

#     values.append(
#         [
#             "TOTAL",
#             formatDollar(orderSet.profit),
#             formatDollar(orderSet.costs),
#             formatNumber(orderSet.totalVolume),
#             formatDollar(orderSet.speculative),
#         ]
#     )

#     return formatTable(headers, values, num)


client_data = ClientData()

@client.slash_command()
async def ask_matching(
    ctx: disnake.ApplicationCommandInteraction,
    question: MatchingQuestion = commands.Param(choices=client_data.game_state.get_matching_question()),
):
    assert client_data.game_state is not None
    await client_data.game_state.ask_question(question)


client.run(TOKEN)
