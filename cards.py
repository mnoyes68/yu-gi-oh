import random
import copy

class Card():
    def __init__(self, name, card_id):
        self.name = name
        self.card_id = card_id

class MonsterCard(Card):
    card_type = "Monster"

    def __init__(self, name, card_id, atk, defn, level):
        Card.__init__(self, name, card_id)
        self.atk = atk
        self.defn = defn
        self.level = level
        self.attacked_this_turn = False

class Deck():
    def __init__(self, cards):
        self.cards = cards
        self.shuffle()


    def shuffle(self):
        random.shuffle(self.cards)


    def add_card(self, card):
        self.cards.append(card)


class Hand():
    def __init__(self):
        self.cards = []


    def add_card(self, card):
        self.cards.append(card)
        return self.cards


    def remove_card(self, card):
        self.cards.remove(card)


    def get_cards(self):
        return self.cards


    def get_size(self):
        return len(self.cards)



