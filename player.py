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
    players: List[PlayerModel]
    tournament_id: str
    game_id: str
    round: int
    bet_index: int
    small_blind: int
    orbits: int
    dealer: int
    community_cards: List[Card]
    current_buy_in: int
    pot: int


class Card(BaseModel):
    rank: str  # 2-10, J, Q, K, A
    suit: str  # hearts, diamonds, clubs, spades

    def converted_rank(self) -> str:
        """return T if 10 else return rank"""
        return self.rank if self.rank != "10" else "T"


class Player:
    VERSION = "Default Python folding player (special version v2)"

    def betRequest(self, game_state):
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
    assert (Card(rank="10", suit="hearts").converted_rank() == "T")

    # Assert Hand representation
    assert (str(Hand([Card(rank="10", suit="hearts"), Card(rank="K", suit="hearts")])) == "KTs")

    # Assert top 20% hands
    assert (is_top_twenty_percent_range(Card(rank="A", suit="hearts"), Card(rank="K", suit="hearts")))
