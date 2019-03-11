import logging
import random
import copy

class Card():
    def __init__(self, name, card_id):
        self.name = name
        self.card_id = card_id


    def __eq__(self, other):
        if isinstance(other, Card):
            return self.card_id == other.card_id
        return False


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return hash("Card:" + self.card_id)


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
        logging.debug('Adding ' + card.name)
        self.cards.append(card)


    def get_size(self):
        return len(self.cards)


class Hand():
    def __init__(self):
        self.cards = []


    def add_card(self, card):
        logging.debug('Adding ' + card.name)
        self.cards.append(card)
        return self.cards


    def remove_card(self, card):
        logging.debug('Removing ' + card.name)
        self.cards.remove(card)


    def get_cards(self):
        return self.cards


    def get_size(self):
        return len(self.cards)


    def __eq__(self, other):
        if isinstance(other, Hand):
            if self.get_size() != other.get_size():
                return False
            my_cards = sorted(self.get_cards(), key=lambda x: x.card_id)
            op_cards = sorted(other.get_cards(), key=lambda x: x.card_id)
            return my_cards == op_cards
        return False


    def __ne__(self, other):
        return not self.__eq__(other)



