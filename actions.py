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
        if self.monster in self.player.hand.cards:
            return True
        else:
            return False

    def execute_move(self):
        if self.check_validity() == False:
            return
        card = self.monster
        self.player.hand.cards.remove(self.monster)
        for space in self.player.board.monster_spaces:
            if space.occupied == False:
                space.add_card(card)
        print "Summoning " + card.name
