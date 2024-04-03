from __future__ import annotations

import json
import logging
import sys
from typing import List

import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

from enum import Enum, IntEnum
from typing import List
from pydantic import BaseModel
from ranges import top_twenty_percent_hands


class GameRound(IntEnum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3


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
    hole_cards: List[Card] | None = None
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

    def game_round(self) -> GameRound:
        community_cards_count = len(self.community_cards)

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

    def is_preflop(self) -> bool:
        return self.game_round() == GameRound.PREFLOP

    def in_action_player(self) -> PlayerModel:
        return self.players[self.in_action]



class Card(BaseModel):
    rank: str  # 2-10, J, Q, K, A
    suit: str  # hearts, diamonds, clubs, spades

    def converted_rank(self) -> str:
        """return T if 10 else return rank"""
        return self.rank if self.rank != "10" else "T"


class Player:
    VERSION = "Default Python folding player (special version v4)"

    def betRequest(self, game_state):
        py_game_state = GameState.model_validate(game_state)

        my_index = game_state["in_action"]
        my_player = game_state["players"][my_index]
        my_stack = my_player["stack"]

        card_a, card_b = self.my_cards(game_state)

        if self.is_preflop(game_state):
            if is_top_twenty_percent_range(card_a, card_b):
                logger.debug("it is preflop and i'm in range")
                return self.determine_preflop_bet(game_state)
            else:
                logger.debug("it is preflop and i'm folding")
                return 0

        rank_service = RankingService()
        my_rank = rank_service.get_rank_for_game_state(py_game_state)

        if my_rank >= 2:
            logger.debug("i think i have a made hand, all in")
            return self.raise_all_in(game_state)
        elif my_rank == 1:
            logger.debug("i have a strong hand, call")
            return self.call(game_state)
        else:
            logger.debug("i have nothing, fold")
            return 0

        # if is_top_twenty_percent_range(card_a, card_b):
        #     logger.debug("I'm going all in!")
        #     return my_stack
        # else:
        #     logger.debug("I'm folding!")
        #     return 0

    def showdown(self, game_state):
        pass

    def determine_preflop_bet(self, game_state):
        current_buy_in = game_state["current_buy_in"]
        small_blind = game_state["small_blind"]
        if current_buy_in <= small_blind * 2:
            logger.debug("I'm raising 3x the small blind")
            return self.raise_(game_state, small_blind * 6)
        else:
            logger.debug("I'm calling in preflop")
            return self.call(game_state)

    def my_cards(self, game_state) -> (Card, Card):
        my_index = game_state["in_action"]
        my_player = game_state["players"][my_index]

        my_cards = my_player["hole_cards"]
        card_a = Card(**my_cards[0])
        card_b = Card(**my_cards[1])

        return (card_a, card_b)

    def call(self, game_state):
        """Returns the amount of chips to call."""
        buy_in = game_state["current_buy_in"]
        bet = game_state["players"][game_state["in_action"]]["bet"] or 0

        return buy_in - bet

    def raise_(self, game_state, amount: int):
        """Returns the amount of chips to raise."""

        return self.call(game_state) + amount

    def raise_all_in(self, game_state):
        my_index = game_state["in_action"]
        my_player = game_state["players"][my_index]
        my_stack = my_player["stack"]

        return my_stack

    def is_preflop(self, game_state) -> bool:
        return get_game_round(len(game_state["community_cards"])) == GameRound.PREFLOP

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

    return str(Hand([a, b])) in top_twenty_percent_hands


class RankingService:
    def get_rank_for_game_state(self, game_state: GameState) -> int:
        cards = []
        for card in game_state.community_cards:
            cards += card

        for card in game_state.in_action_player().hole_cards:
            cards += card

        return self.rank(cards)

    def rank(self, cards: List[Card]) -> int:


        all_cards = [{"rank": c.rank, "suit": c.suit} for c in cards]
        try:
            response = requests.get("https://rainman.leanpoker.org/rank", params={"cards": json.dumps(all_cards)}, timeout=10)
        except Exception as e:
            logger.error(e)
            logger.error("could not retrieve ranking")
            return 0

        if response.status_code != 200:
            logger.error(f"could not retrieve ranking (non 200) {response.status_code}")
            return 0

        ranks = response.json()
        try:
            logger.debug(f"ranked my hand as {ranks['rank']}")
            return int(ranks["rank"])
        except Exception:
            logger.error("could not parse ranking")
            return 0



if __name__ == '__main__':
    # Assert "10" is converted to "T"
    assert(Card(rank="10", suit="hearts").converted_rank() == "T")

    # Assert Hand representation
    assert(str(Hand([Card(rank="10", suit="hearts"), Card(rank="K", suit="hearts")])) == "KTs")

    # Assert top 20% hands
    assert(is_top_twenty_percent_range(Card(rank="A", suit="hearts"), Card(rank="K", suit="hearts")))

    # Assert is not top 20% hands
    assert(not is_top_twenty_percent_range(Card(rank="2", suit="hearts"), Card(rank="3", suit="hearts")))

    # Assert GameRound
    assert(GameRound(0) == GameRound.PREFLOP)
    assert(GameRound(3) == GameRound.RIVER)


    # Assert GameState
    game_state_data = """
{
  "in_action": 0,
  "players": [
    {
      "name": "Player 1",
      "stack": 1000,
      "status": "active",
      "bet": 0,
      "hole_cards": [
        {
          "rank": "6",
          "suit": "hearts"
        },
        {
          "rank": "K",
          "suit": "spades"
        }
      ],
      "version": "Version name 1",
      "id": 0
    },
    {
      "name": "Player 2",
      "stack": 1000,
      "status": "active",
      "bet": 0,
      "version": "Version name 2",
      "id": 1
    }
  ],
  "tournament_id": "550d1d68cd7bd10003000003",
  "game_id": "550da1cb2d909006e90004b1",
  "round": 0,
  "bet_index": 0,
  "small_blind": 10,
  "orbits": 0,
  "dealer": 0,
  "community_cards": [],
  "current_buy_in": 0,
  "pot": 0
}
    """
    dict_state = json.loads(game_state_data)

    player = Player()
    bet = player.betRequest(dict_state)
    assert isinstance(bet, int)
    assert bet >= 0

    state = GameState.model_validate(dict_state)

    assert(state.game_round() == GameRound.PREFLOP)
    assert(state.is_preflop())
    assert(state.in_action_player().name == "Player 1")
    assert(state.in_action_player().stack == 1000)
    assert(state.in_action_player().hole_cards == [Card(rank="6", suit="hearts"), Card(rank="K", suit="spades")])

    state.community_cards = [Card(rank="A", suit="hearts"), Card(rank="K", suit="hearts"), Card(rank="Q", suit="hearts")]
    assert(state.game_round() == GameRound.FLOP)

    rank = RankingService()
    ranked = rank.rank([
        Card(rank="A", suit="diamonds"),
        Card(rank="A", suit="clubs"),
        Card(rank="A", suit="hearts"),
        Card(rank="A", suit="spades"),
        Card(rank="2", suit="spades"),
    ])
    assert ranked == 7

    rank = RankingService()
    ranked = rank.rank([
        Card(rank="A", suit="diamonds"),
        Card(rank="A", suit="clubs"),
        Card(rank="A", suit="hearts"),
        Card(rank="A", suit="spades"),
        Card(rank="2", suit="spades"),
        Card(rank="3", suit="spades"),
        Card(rank="4", suit="spades"),
    ])
    assert ranked == 7


    
