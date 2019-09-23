import numpy as np

import logging

class Action():
    def __init__(self, is_sim=False):
        self.is_sim = is_sim

    def get_name(self):
        return ""

    def get_canvas(self):
        shape = (2,20)
        canvas = np.zeros(shape)
        return canvas


class DrawCard(Action):
    def __init__(self, player, is_sim=False):
        Action.__init__(self, is_sim)
        self.player = player


    def get_name(self):
        return "Draw Card"


    def execute_move(self):
        self.player.draw_card()
        return False


    def __eq__(self, other):
        return isinstance(other, DrawCard)


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return hash("DrawCard")


class AdvanceTurn(Action):
    def __init__(self, is_sim=False):
        Action.__init__(self, is_sim)


    def get_name(self):
        return "Advance Turn"


    def execute_move(self):
        return False


    def __eq__(self, other):
        return isinstance(other, AdvanceTurn)


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return hash("AdvanceTurn")


class NormalSummon(Action):
    def __init__(self, player, monster, is_sim=False):
        Action.__init__(self, is_sim)
        self.player = player
        self.monster = monster


    def get_name(self):
        return " Normal Summon " + self.monster.name


    def check_validity(self):
        if self.monster not in self.player.hand.cards:
            return False
        if self.player.board.get_occupied_monster_spaces() >= 5:
            return False
        return True


    def execute_move(self):
        if not self.check_validity():
            return False
        card = self.monster
        self.player.hand.cards.remove(self.monster)
        for space in self.player.board.monster_spaces:
            if not space.occupied:
                space.add_card(card)
                break
        message = "Summoning " + card.name
        if self.is_sim:
            logging.debug(message)
        else:
            logging.info(message)
        return True


class Attack(Action):
    def __init__(self, player, opponent, monster, target, is_sim=False):
        Action.__init__(self, is_sim)
        self.player = player
        self.opponent = opponent
        self.monster = monster
        self.target = target

    def get_name(self):
        return "Attack {0} ({1}) with {2} ({3})".format(self.target.name, self.target.atk, self.monster.name, self.monster.atk)

    def check_validity(self):
        if self.monster not in self.player.board.get_monsters():
            return False
        if self.target not in self.opponent.board.get_monsters():
            return False
        return True

    def execute_move(self):
        if not self.check_validity():
            return False
        message = "Attacking " + self.target.name + " with " + self.monster.name
        if self.is_sim:
            logging.debug(message)
        else:
            logging.info(message)
        self.process_attack()
        self.monster.attacked_this_turn = True
        return True

    def process_attack(self):
        if self.monster.atk > self.target.atk:
            diff = self.monster.atk - self.target.atk
            self.opponent.board.destroy_monster(self.target)
            self.opponent.decrease_life_points(diff)
        elif self.monster.atk < self.target.atk:
            diff = self.target.atk - self.monster.atk
            self.player.board.destroy_monster(self.monster)
            self.player.decrease_life_points(diff)
        elif self.monster.atk == self.target.atk:
            self.opponent.board.destroy_monster(self.target)
            self.player.board.destroy_monster(self.monster)


    def __eq__(self, other):
        if isinstance(other, Attack):
            return self.monster == other.monster and self.target == other.target
        return False


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return hash("Attack:" + self.monster.card_id + ":" + self.target.card_id)


class DirectAttack(Action):
    def __init__(self, player, opponent, monster, is_sim=False):
        Action.__init__(self, is_sim)
        self.player = player
        self.opponent = opponent
        self.monster = monster

    def get_name(self):
        return "Attack {0} directly with {1} ({2})".format(self.opponent.name, self.monster.name, self.monster.atk)

    def check_validity(self):
        if self.opponent.board.get_occupied_monster_spaces() > 0:
            return False
        if self.player.board.get_occupied_monster_spaces() <= 0:
            return False
        return True

    def execute_move(self):
        if not self.check_validity():
            return False
        message = "Attacking " + self.opponent.name + " directly with " + self.monster.name
        if self.is_sim:
            logging.debug(message)
        else:
            logging.info(message)
        self.opponent.decrease_life_points(self.monster.atk)
        self.monster.attacked_this_turn = True
        return True


    def __eq__(self, other):
        if isinstance(other, DirectAttack):
            return self.monster == other.monster
        return False


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return hash("DirectAttack:" + self.monster.card_id)


