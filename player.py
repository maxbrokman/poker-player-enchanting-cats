from __future__ import annotations

import logging
import sys
from typing import List
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

from enum import Enum
from typing import List
from pydantic import BaseModel

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
    rank: str # 2-10, J, Q, K, A
    suit: str # hearts, diamonds, clubs, spades

    def coverted_rank(self) -> str:
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


def is_top_twenty_percent_range(a: Card, b: Card) -> bool:
    """Returns True if the two cards are in the top 20% of hands."""
    is_same_suit = a.suit == b.suit
    is_pair = a.rank == b.rank

    order = "23456789TJQKA"
    a_index = order.index(a.coverted_rank())
    b_index = order.index(b.coverted_rank())

    first_card = a if a_index > b_index else b
    second_card = b if a_index > b_index else a

    # eg "AKs", "QJs", "T9o"
    repr = f"{first_card.rank}{second_card.rank}{'s' if is_same_suit else 'o'}"

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

    logger.debug(f"Checking if {repr} is in top 20% hands: {repr in top_twenty_percent_hands}")


    return repr in top_twenty_percent_hands





