import random

class Card():
    def __init__(self, name, card_id):
        self.name = name
        self.card_id = card_id

class MonsterCard(Card):
    card_type = "Monster"

    def __init__(self, name, card_id, atk, defn):
        Card.__init__(self, name, card_id)
        self.atk = atk
        self.defn = defn

class Deck():
    def __init__(self, cards):
        self.cards = cards
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

class Hand():
    def __init__(self):
        self.hand = []

    def add_card(self, card):
        self.hand.append(card)
        return self.hand