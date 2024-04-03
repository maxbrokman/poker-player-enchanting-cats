from __future__ import annotations
from typing import List
from pydantic import BaseModel

class PlayerModel(BaseModel):
    name: str
    stack: int
    status: str
    bet: int
    hole_cards: List[Card]
    version: str
    id: int

class GameState(BaseModel):
    players: List[Player]
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
    rank: str
    suit: str

class Player:
    VERSION = "Default Python folding player (special version v2)"

    def betRequest(self, game_state):
        my_index = game_state["in_action"]
        my_player = game_state["players"][my_index]
        my_stack = my_player["stack"]

        return my_stack

    def showdown(self, game_state):
        pass

