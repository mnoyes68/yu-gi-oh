import cards
import decisionmanager

import logging

class Player():
    def __init__(self, name, deck, is_sim=False):
        self.name = name
        self.deck = deck
        self.hand = cards.Hand()
        self.board = Board(is_sim=is_sim)
        self.life_points = 4000
        self.is_sim = is_sim
        self.memory = []
        #self.decisionmanager = decisionmanager.DecisionManager()


    def draw_card(self):
        c = self.deck.cards.pop(0)
        self.hand.cards.append(c)
        message = self.name + " drew " + c.name
        if self.is_sim:
            logging.debug(message)
        else:
            logging.info(message)


    def increase_life_points(self, amount):
        self.life_points += amount


    def decrease_life_points(self, amount):
        self.life_points -= amount
        if self.life_points <= 0:
            self.life_points = 0
            if self.is_sim:
                logging.debug("GAME OVER!")
            else:
                logging.info("GAME OVER!")
        message = self.name + "'s life points are now " + str(self.life_points)
        if self.is_sim:
            logging.debug(message)
        else:
            logging.info(message)


    def set_as_sim(self):
        self.is_sim = True
        self.board.is_sim = True

class Board():
    def __init__(self, is_sim=False):
        self.monster_spaces = []
        self.magic_trap_spaces = []
        self.graveyard = []
        self.is_sim = is_sim
        for i in range(0,5):
            self.monster_spaces.append(Space("Monster"))
            self.magic_trap_spaces.append(Space("Magic-Trap"))


    def get_occupied_monster_spaces(self):
        occupied_spaces = [s for s in self.monster_spaces if s.occupied == True]
        return len(occupied_spaces)


    def get_monsters(self):
        return [s.card for s in self.monster_spaces if s.occupied == True]


    def destroy_monster(self, monster):
        for space in self.monster_spaces:
            if monster == space.card:
                space.remove_card()
                self.graveyard.append(monster)
                message = monster.name + " is now destroyed"
                if self.is_sim:
                    logging.debug(message)
                else:
                    logging.info(message)
                break

class Space():
    def __init__(self, card_type):
        self.card_type = card_type
        self.occupied = False
        self.card = None

    def add_card(self, card):
        self.card = card
        self.occupied = True

    def remove_card(self):
        self.card = None
        self.occupied = False

class ComputerPlayer(Player):
    player_type = "Computer"

    def __init__(self, name, deck, model):
        Player.__init__(self, name, deck)
        if(model == None):
            self.decisionmanager = decisionmanager.DecisionManager()
        else:
            self.decisionmanager = decisionmanager.NetworkDecisionManager(model)


