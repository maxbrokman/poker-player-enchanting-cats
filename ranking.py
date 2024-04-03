from typing import List

from pydantic import BaseModel

class Card(BaseModel):
    rank: str  # 2-10, J, Q, K, A
    suit: str  # hearts, diamonds, clubs, spades

    def converted_rank(self) -> str:
        """return T if 10 else return rank"""
        return self.rank if self.rank != "10" else "T"

    def score(self) -> int:
        order = "23456789TJQKA"
        return order.index(self.converted_rank())

    @staticmethod
    def from_string(card: str):
        """
        Create a card from a string representation
        Example: 
            - "2h" -> Card(rank="2", suit="hearts")
            - "10d" -> Card(rank="10", suit="diamonds")
        """
        rank = card[:-1]
        suit = card[-1]
        return Card(rank=rank, suit=suit)

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

    @staticmethod
    def from_string(hand: str):
        """
        Create a hand from a string representation
        Example: 
            - "2h 3h" -> Hand([Card(rank="2", suit="hearts"), Card(rank="3", suit="hearts")])
        """

        cards = [Card.from_string(card) for card in hand.split()]
        return Hand(cards)


def get_rank(hand: Hand) -> int:
    """
    Calculate the rank of the hand
    
    Checks for the following hands in descending order:
    - Royal Flush
    - Straight Flush
    - Four of a Kind
    - Full House
    - Flush
    - Straight
    - Three of a Kind
    - Two Pair
    - Pair
    - High cards
    """

    # check for straight
    order = "23456789TJQKA"
    ranks = sorted([card.score() for card in hand.cards])
    is_straight = ranks == list(range(ranks[0], ranks[0] + 5))

    # check for flush
    is_flush = all([card.suit == hand.cards[0].suit for card in hand.cards])

    # check for pairs
    pairs = {}
    for card in hand.cards:
        if card.converted_rank() in pairs:
            pairs[card.converted_rank()] += 1
        else:
            pairs[card.converted_rank()] = 1

    # check for four of a kind
    if 4 in pairs.values():
        return 8

    # check for full house
    if 3 in pairs.values() and 2 in pairs.values():
        return 7

    # check for three of a kind
    if 3 in pairs.values():
        return 4

    # check for two pairs
    if list(pairs.values()).count(2) == 2:
        return 3

    # check for pair
    if 2 in pairs.values():
        return 2

    # check for straight flush
    if is_straight and is_flush:
        return 9

    # check for flush
    if is_flush:
        return 6

    # check for straight
    if is_straight:
        return 5

    return 1  # high card 

if __name__ == "__main__":
    # test the code
    royal_flush = Hand.from_string("Ah Kh Qh Jh Th")
    straight_flush = Hand.from_string("9h 8h 7h 6h 5h")
    four_of_a_kind = Hand.from_string("2h 2d 2c 2s 3h")
    full_house = Hand.from_string("2h 2d 2c 3s 3h")
    flush = Hand.from_string("2h 4h 6h 8h Th")
    straight = Hand.from_string("2h 3d 4c 5s 6h")
    three_of_a_kind = Hand.from_string("2h 2d 2c 3s 4h")
    two_pair = Hand.from_string("2h 2d 3c 3s 4h")
    pair = Hand.from_string("2h 2d 3c 4s 5h")
    high_cards = Hand.from_string("2h 3d 4c 5s 7h")

    assert(get_rank(royal_flush) == 9)
    assert(get_rank(straight_flush) == 9)
    assert(get_rank(four_of_a_kind) == 8)
    assert(get_rank(full_house) == 7)
    assert(get_rank(flush) == 6)
    assert(get_rank(straight) == 5)
    assert(get_rank(three_of_a_kind) == 4)
    assert(get_rank(two_pair) == 3)
    assert(get_rank(pair) == 2)
    assert(get_rank(high_cards) == 1)
    print("All tests passed!")
