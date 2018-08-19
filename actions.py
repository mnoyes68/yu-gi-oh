import cards
import player

class Action():
    def __init__(self):
        pass


class NormalSummon():
    def __init__(self, player, monster):
        self.player = player
        self.monster = monster

    def check_validity(self):
        if self.monster not in self.player.hand.cards:
            return False
        if self.player.board.get_occupied_monster_spaces() >= 5:
            return False
        return True

    def execute_move(self):
        if self.check_validity() == False:
            return False
        card = self.monster
        self.player.hand.cards.remove(self.monster)
        for space in self.player.board.monster_spaces:
            if space.occupied == False:
                space.add_card(card)
                break
        print "Summoning " + card.name
        return True

class Attack():
    def __init__(self, player, opponent, monster, target):
        self.player = player
        self.opponent = opponent
        self.monster = monster
        self.target = target

    def check_validity(self):
        if self.monster not in self.player.board.get_monsters():
            return False
        if self.target not in self.opponent.board.get_monsters():
            return False
        return True

    def execute_move(self):
        if self.check_validity() == False:
            return False
        print "Attacking " + self.target.name + " with " + self.monster.name
        self.process_attack()
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

class DirectAttack():
    def __init__(self, player, opponent, monster):
        self.player = player
        self.opponent = opponent
        self.monster = monster

    def check_validity(self):
        if self.opponent.board.get_occupied_monster_spaces() > 0 :
            return False
        if self.player.board.get_occupied_monster_spaces() <= 0:
            return False
        return True

    def execute_move(self):
        if self.check_validity() == False:
            return False
        print "Attacking " + self.opponent.name + " directly with " + self.monster.name
        self.opponent.decrease_life_points(self.monster.atk)
        return True
