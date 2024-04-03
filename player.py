from __future__ import annotations

import logging
import sys
from typing import List
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

from enum import Enum, StrEnum
from typing import List
from pydantic import BaseModel


class GameRound(StrEnum):
    PREFLOP = 'preflop'
    FLOP = 'flop'
    TURN = 'turn'
    RIVER = 'river'


def get_game_round(community_cards_count: int) -> GameRound:
    if community_cards_count == 0:
        return GameRound.PREFLOP
    if community_cards_count == 3:
        return GameRound.FLOP
    if community_cards_count == 4:
        return GameRound.TURN
    if community_cards_count == 5:
        return GameRound.RIVER

    logger.error("could not get game round")
    raise ValueError("ouch")


class PlayerPosition(Enum):
    BUTTON = "button"
    BIG_BLIND = "big_blind"
    SMALL_BLIND = "small_blind"
    UNDER_THE_GUN = "under_the_gun"
    OTHER = "other"


class PlayerModel(BaseModel):
    name: str
    stack: int
    status: str
    bet: int
    hole_cards: List[Card]
    version: str
    id: int


class GameState(BaseModel):
    players: List[PlayerModel] # An array of the players. The order stays the same during the entire game.
    round: int # the round number
    small_blind: int # the small blind in the current round
    orbits: int # number of orbits completed in the tournament
    dealer: int # index of the dealer
    community_cards: List[Card] # community cards
    current_buy_in: int # the amount of the largest current bet from any one player
    pot: int # total pot
    in_action: int # index of the player who is currently making a bet


class Card(BaseModel):
    rank: str  # 2-10, J, Q, K, A
    suit: str  # hearts, diamonds, clubs, spades

    def converted_rank(self) -> str:
        """return T if 10 else return rank"""
        return self.rank if self.rank != "10" else "T"


class Player:
    VERSION = "Default Python folding player (special version v2)"

    def betRequest(self, game_state):
        community_cards = game_state["community_cards"]
        game_round = get_game_round(len(community_cards))

        my_index = game_state["in_action"]
        my_player = game_state["players"][my_index]
        my_stack = my_player["stack"]

        my_cards = my_player["hole_cards"]
        card_a = Card(**my_cards[0])
        card_b = Card(**my_cards[1])

        if is_top_twenty_percent_range(card_a, card_b):
            logger.debug("I'm going all in!")
            return my_stack
        else:
            logger.debug("I'm folding!")
            return 0

    def showdown(self, game_state):
        pass

class Hand:
    def __init__(self, cards: List[Card]):
        self.cards = cards

    def __repr__(self):
        # rank order
        order = "23456789TJQKA"

        # sort cards by rank
        sorted_cards = sorted(self.cards, key=lambda card: order.index(card.converted_rank()), reverse=True)

        # check if every cards have same suit
        is_same_suit = all([card.suit == self.cards[0].suit for card in self.cards])

        # build the rank representation
        repr = "".join([card.converted_rank() for card in sorted_cards]) + ('s' if is_same_suit else 'o')

        return repr


def is_top_twenty_percent_range(a: Card, b: Card) -> bool:
    """Returns True if the two cards are in the top 20% of hands."""

    top_twenty_percent_hands = [
        "AAo",
        "KKo",
        "QQo",
        "JJo",
        "TTo",
        "99o",
        "88o",
        "77o",
        "66o",
        "55o",
        "44o",

        "AKs",
        "AQs",
        "AJs",
        "ATs",
        "ATs",
        "A9s",
        "A8s",
        "A7s",
        "A6s",
        "A5s",
        "A4s",
        "A3s",
        "A2s",

        "AKo",
        "AQo",
        "AJo",
        "ATo",

        "KQo",
        "KJo",
        "KQs",
        "KJs",
        "KTs",
        "K9s",

        "QJs",
        "QTs",
        "Q9s",

        "JTs",
        "J9s",
        "T9s",
        "98s",
        "87s",
        "76s",
        "65s",
    ]

    return str(Hand([a, b])) in top_twenty_percent_hands

if __name__ == '__main__':
    # Assert "10" is converted to "T"
    assert(Card(rank="10", suit="hearts").converted_rank() == "T")

    # Assert Hand representation
    assert(str(Hand([Card(rank="10", suit="hearts"), Card(rank="K", suit="hearts")])) == "KTs")

    # Assert top 20% hands
    assert(is_top_twenty_percent_range(Card(rank="A", suit="hearts"), Card(rank="K", suit="hearts")))

    # Assert is not top 20% hands
    assert(not is_top_twenty_percent_range(Card(rank="2", suit="hearts"), Card(rank="3", suit="hearts")))
