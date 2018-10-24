import cards
import player
import actions
import random
import decisionmanager

#decision_manager = decisionmanager.DecisionManager()

class Game():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        #self.turn = self.p1
        self.turn_number = 1
        self.winner = None

    def play_game(self):
        self.initialize_game()
        print '\n' + "BEGIN GAME!!!" + '\n'
        coin_flip = self.flip_coin()
        if coin_flip == 0:
            self.turn = self.p1 
        else:
            self.turn = self.p2
        print self.turn.name + " goes first"
        while self.p1.life_points > 0 and self.p2.life_points > 0 and len(self.p1.deck.cards) > 0 and len(self.p2.deck.cards) > 0:
            if self.turn == self.p1:
                self.play_turn(self.turn, self.p2)
            else:
                self.play_turn(self.turn, self.p1)
            if self.p1.life_points <= 0 or self.p2.life_points <= 0:
                break
            self.change_turn()
            self.turn_number += 1
        self.declare_winner()

    def flip_coin(self):
        return random.randint(0, 1)

    def play_turn(self, player, opponent):
        #print "It is now " + player.name + "'s Turn"
        dp = DrawPhase(player)
        dp.execute_phase()

        mp = MainPhase(player)
        mp.execute_phase()

        if self.turn_number > 1:
            bp = BattlePhase(player, opponent)
            bp.execute_phase()

        mp2 = MainPhase2(player)
        mp2.execute_phase()

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

    def declare_winner(self):
        if self.p1.life_points <= 0 or len(self.p1.deck.cards) <= 0:
            self.winner = self.p2
        elif self.p2.life_points <= 0 or len(self.p2.deck.cards) <= 0:
            self.winner = self.p1

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
        card_choice = self.player.decisionmanager.make_decision(self.player.hand.cards)
        move = actions.NormalSummon(self.player, card_choice)
        move.execute_move()

class BattlePhase(Phase):
    def __init__(self, player, opponent):
        Phase.__init__(self, player)
        self.opponent = opponent

    def get_valid_moves(self):
        move_list = []
        move_list.append(actions.AdvanceTurn())
        if self.opponent.board.get_occupied_monster_spaces() == 0:
            for monster in self.player.board.get_monsters():
                if monster.attacked_this_turn == False:
                    move = actions.DirectAttack(self.player, self.opponent, monster)
                    move_list.append(move)
        else:
            for monster in self.player.board.get_monsters():
                if monster.attacked_this_turn == False:
                    for target in self.opponent.board.get_monsters():
                        move = actions.Attack(self.player, self.opponent, monster, target)
                        move_list.append(move)
        return move_list

    def execute_phase(self):
        while True:
            move_list = self.get_valid_moves()
            print str(len(move_list)) + " valid moves"
            move = self.player.decisionmanager.make_network_decision(move_list)
            self.player.memory.append(move.draw_state().reshape((1, -1)))
            if move.__class__.__name__ == "AdvanceTurn":
                break
            move.execute_move()
            if self.player.life_points <= 0 or self.opponent.life_points <= 0:
                break

class MainPhase2(Phase):
    def execute_phase(self):
        for monster in self.player.board.get_monsters():
            monster.attacked_this_turn == False




