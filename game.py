import cards
import player

class Game():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.turn = self.p1

    def play_game(self):
        self.initialize_game()
        print '\n' + "BEGIN GAME!!!" + '\n'
        while self.p1.life_points > 0 and self.p2.life_points > 0 and len(self.p1.deck.cards) > 0 and len(self.p2.deck.cards) > 0:
            self.play_turn(self.p1)
            self.play_turn(self.p2)

    def play_turn(self, player):
        print "It is now " + player.name + "'s Turn"
        player.draw_card()

    def initialize_game(self):
        for i in range (0,5):
            self.p1.draw_card()
            self.p2.draw_card()

    def change_turn(self):
        if self.turn == self.p1:
            self.turn == self.p2
        else:
            self.turn == self.p1
        print '\n' + "It is now " + self.turn.name + "'s Turn" + '\n'

class Board():
    def __init__(self):
        pass

class Space():
    def __init__(self, type, player):
        self.type = type
        self.player = player
