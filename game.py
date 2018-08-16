import cards
import player
import actions
import random
import decisionmanager

class Game():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.decision_manager = decisionmanager.Decisionmaker()
        self.turn = self.p1

    def play_game(self):
        self.initialize_game()
        print '\n' + "BEGIN GAME!!!" + '\n'
        while self.p1.life_points > 0 and self.p2.life_points > 0 and len(self.p1.deck.cards) > 0 and len(self.p2.deck.cards) > 0:
            self.play_turn(self.p1)
            self.play_turn(self.p2)

    def play_turn(self, player):
        print "It is now " + player.name + "'s Turn"
        dp = DrawPhase(player)
        dp.execute_phase()
        mp = MainPhase(player)
        mp.execute_phase()

    def initialize_game(self):
        for i in range (0,5):
            self.p1.draw_card()
            self.p2.draw_card()

    def change_turn(self):
        if self.turn == self.p1:
            self.turn == self.p2
        else:
            self.turn == self.p1
        print "It is now " + self.turn.name + "'s Turn"

class Phase():
    def __init__(self, player):
        self.player = player

    def execute_phase(self):
        raise NotImplementedError('users must define execute to use this base class')

class DrawPhase(Phase):
    def execute_phase(self):
        self.player.draw_card()

class MainPhase(Phase):
    def execute_phase(self):
        card_choice = random.choice(self.player.hand.cards)
        move = actions.NormalSummon(self.player, card_choice)
        move.execute_move()





