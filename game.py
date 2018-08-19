import cards
import player
import actions
import random
import decisionmanager

decision_manager = decisionmanager.DecisionManager()

class Game():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.turn = self.p1
        self.turn_number = 1

    def play_game(self):
        self.initialize_game()
        print '\n' + "BEGIN GAME!!!" + '\n'
        while self.p1.life_points > 0 and self.p2.life_points > 0 and len(self.p1.deck.cards) > 0 and len(self.p2.deck.cards) > 0:
            if self.turn == self.p1:
                self.play_turn(self.turn, self.p2)
            else:
                self.play_turn(self.turn, self.p1)
            self.change_turn()
            self.turn_number += 1

    def play_turn(self, player, opponent):
        #print "It is now " + player.name + "'s Turn"
        dp = DrawPhase(player)
        dp.execute_phase()

        mp = MainPhase(player)
        mp.execute_phase()

        if self.turn_number > 1:
            bp = BattlePhase(player, opponent)
            bp.execute_phase()

    def initialize_game(self):
        for i in range (0,5):
            self.p1.draw_card()
            self.p2.draw_card()

    def change_turn(self):
        if self.turn == self.p1:
            self.turn = self.p2
        else:
            self.turn = self.p1
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
        card_choice = decision_manager.make_decision(self.player.hand.cards)
        move = actions.NormalSummon(self.player, card_choice)
        move.execute_move()

class BattlePhase(Phase):
    def __init__(self, player, opponent):
        Phase.__init__(self, player)
        self.opponent = opponent

    def execute_phase(self):
        monster_choice = decision_manager.make_decision(self.player.board.get_monsters())
        if self.opponent.board.get_occupied_monster_spaces() == 0:
            move = actions.DirectAttack(self.player, self.opponent, monster_choice)
            move.execute_move()
        else:
            target_choice = decision_manager.make_decision(self.opponent.board.get_monsters())
            move = actions.Attack(self.player, self.opponent, monster_choice, target_choice)
            move.execute_move()




