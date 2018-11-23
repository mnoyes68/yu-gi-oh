import numpy as np


class Action():
    def __init__(self):
        pass

    def get_name(self):
        return ""

    def get_canvas(self):
        shape = (2,20)
        canvas = np.zeros(shape)
        return canvas

    def draw_state(self):
        canvas = self.get_canvas()
        return canvas


class AdvanceTurn(Action):
    def __init__(self):
        pass

    def get_name(self):
        return "Advance Turn"

    def execute_move(self):
        return False


class NormalSummon(Action):
    def __init__(self, player, monster):
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
        print "Summoning " + card.name
        return True


class Attack(Action):
    def __init__(self, player, opponent, monster, target):
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
        print "Attacking " + self.target.name + " with " + self.monster.name
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

    def draw_state(self):
        canvas = self.get_canvas()
        i, j = 0, 0
        canvas[i, j] = 1
        j += 1
        canvas[i, j] = self.monster.level
        j += 1
        canvas[i, j] = self.monster.atk
        j += 1
        canvas[i, j] = self.monster.defn
        j += 1

        for mnstr in self.player.board.get_monsters():
            if mnstr != self.monster:
                canvas[i, j] = 1
                j += 1
                canvas[i, j] = mnstr.level
                j += 1
                canvas[i, j] = mnstr.atk
                j += 1
                canvas[i, j] = mnstr.defn
                j += 1

        # Flip sides
        i += 1
        j=0

        canvas[i, j] = 1
        j += 1
        canvas[i, j] = self.target.level
        j += 1
        canvas[i, j] = self.target.atk
        j += 1
        canvas[i, j] = self.target.defn
        j += 1

        for mnstr in self.opponent.board.get_monsters():
            if mnstr != self.target:
                canvas[i, j] = 1
                j += 1
                canvas[i, j] = mnstr.level
                j += 1
                canvas[i, j] = mnstr.atk
                j += 1
                canvas[i, j] = mnstr.defn
                j += 1
        return canvas


class DirectAttack(Action):
    def __init__(self, player, opponent, monster):
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
        print "Attacking " + self.opponent.name + " directly with " + self.monster.name
        self.opponent.decrease_life_points(self.monster.atk)
        self.monster.attacked_this_turn = True
        return True

    def draw_state(self):
        canvas = self.get_canvas()
        i, j = 0, 0
        canvas[i, j] = 1
        j += 1
        canvas[i, j] = self.monster.level
        j += 1
        canvas[i, j] = self.monster.atk
        j += 1
        canvas[i, j] = self.monster.defn
        j += 1

        for mnstr in self.player.board.get_monsters():
            if mnstr != self.monster:
                canvas[i, j] = 1
                j += 1
                canvas[i, j] = mnstr.level
                j += 1
                canvas[i, j] = mnstr.atk
                j += 1
                canvas[i, j] = mnstr.defn
                j += 1
        return canvas
