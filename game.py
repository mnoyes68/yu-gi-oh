import cards
import player
import actions
import decisionmanager
import statedraw

import copy
import random
import operator
import logging

class Game():
    def __init__(self, p1, p2, is_sim=False):
        self.p1 = p1
        self.p2 = p2
        self.turn_number = 1
        self.winner = None
        self.is_sim = is_sim

    def play_game(self):
        self.initialize_game()
        logging.info('\n' + "BEGIN GAME!!!" + '\n')
        coin_flip = self.flip_coin()
        if coin_flip == 0:
            self.turn = self.p1 
        else:
            self.turn = self.p2
        message = self.turn.name + " goes first"
        if self.is_sim:
            logging.debug(message)
        else:
            logging.info(message)
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
        message = "It is now " + self.turn.name + "'s Turn"
        if self.is_sim:
            logging.debug(message)
        else:
            logging.info(message)

    def declare_winner(self):
        if self.p1.life_points <= 0 or len(self.p1.deck.cards) <= 0:
            self.winner = self.p2
        elif self.p2.life_points <= 0 or len(self.p2.deck.cards) <= 0:
            self.winner = self.p1

class Phase():
    def __init__(self, player, is_sim=False):
        self.player = player
        self.is_sim = is_sim

    def execute_phase(self):
        raise NotImplementedError('users must define execute to use this base class')

class DrawPhase(Phase):
    def __init__(self, player, is_sim=False):
        Phase.__init__(self, player, is_sim)
    def execute_phase(self):
        self.player.draw_card()

class MainPhase(Phase):
    def __init__(self, player, is_sim=False):
        Phase.__init__(self, player, is_sim)


    def execute_phase(self):
        card_choice = self.player.decisionmanager.make_decision(self.player.hand.cards)
        move = actions.NormalSummon(self.player, card_choice, is_sim=self.is_sim)
        move.execute_move()


    def get_valid_moves(self):
        move_list = []
        move_list.append(actions.AdvanceTurn())
        for card in self.player.hand.get_cards():
            if isinstance(card, cards.MonsterCard):
                move = actions.NormalSummon(self.player, card)
                move_list.append(move)
        return move_list


class BattlePhase(Phase):
    def __init__(self, player, opponent, is_sim=False, get_first_move=False):
        Phase.__init__(self, player, is_sim)
        self.opponent = opponent
        self.get_first_move = get_first_move


    def get_valid_moves(self):
        move_list = []
        move_list.append(actions.AdvanceTurn(is_sim=self.is_sim))
        if self.opponent.board.get_occupied_monster_spaces() == 0:
            for monster in self.player.board.get_monsters():
                if monster.attacked_this_turn == False:
                    move = actions.DirectAttack(self.player, self.opponent, monster, is_sim=self.is_sim)
                    move_list.append(move)
        else:
            for monster in self.player.board.get_monsters():
                if monster.attacked_this_turn == False:
                    for target in self.opponent.board.get_monsters():
                        move = actions.Attack(self.player, self.opponent, monster, target, is_sim=self.is_sim)
                        move_list.append(move)
        return move_list


    def execute_phase(self):
        while True:
            self.player.memory.append(statedraw.write_game_state(self.player, self.opponent))
            move_list = self.get_valid_moves()
            message = str(len(move_list)) + " valid moves"
            if self.is_sim:
                logging.debug(message)
            else:
                logging.info(message)

            if not self.is_sim:
                best_move = self.get_best_move() # Tests the game in progress
                for mv in move_list:
                    if best_move == mv:
                        move = mv
                        break
            else:
                move = self.player.decisionmanager.make_decision(move_list)
            
            if self.get_first_move:
                self.chosen_first_move = move # Assigns the first chosen move to the phase to be returned for calculation of the move score
                self.get_first_move = False
            if isinstance(move, actions.AdvanceTurn):
                break
            move.execute_move()
            if self.player.life_points <= 0 or self.opponent.life_points <= 0:
                break


    def get_best_move(self):
        move_occurences = {}
        move_wins = {}
        for i in range(0, 1600):
            simmed_game = self.simulate_game()
            chosen_move = simmed_game.chosen_first_move
            winner = simmed_game.winner

            if chosen_move in move_occurences:
                move_occurences[chosen_move] += 1
            else:
                move_occurences[chosen_move] = 1
                move_wins[chosen_move] = 0

            if winner.name == self.player.name: # Bit of a hack that should be fixed
                move_wins[chosen_move] += 1

        move_scores = {}
        for mv in move_occurences.keys():
            score = move_wins[mv]/float(move_occurences[mv])
            move_scores[mv] = score
            logging.info(mv.get_name() + ": " + str(score))

        return max(move_scores.iteritems(), key=operator.itemgetter(1))[0]


    def simulate_game(self):
        logging.debug("Simulating game")
        p1 = copy.deepcopy(self.player)
        p2 = copy.deepcopy(self.opponent)

        p1.set_as_sim()
        p2.set_as_sim()

        sim_game = GameInProgress(p1, p2, 2, BattlePhase)
        sim_game.play_game()
        return sim_game


class MainPhase2(Phase):
    def __init__(self, player, is_sim=False):
        Phase.__init__(self, player, is_sim)


    def execute_phase(self):
        for monster in self.player.board.get_monsters():
            monster.attacked_this_turn = False


class GameInProgress(Game):
    def __init__(self, player, opponent, turn_number, phase, shuffle_unknown_cards=True):
        Game.__init__(self, player, opponent)
        self.turn_number = turn_number
        self.turn = player
        self.begin_phase = phase
        self.is_sim = True
        if shuffle_unknown_cards:
            self.shuffle_unknown_cards()


    def shuffle_unknown_cards(self):
        opp_hand_size = self.p2.hand.get_size()

        for card in self.p2.hand.get_cards():
            self.p2.hand.remove_card(card)
            self.p2.deck.add_card(card)

        self.p1.deck.shuffle()
        self.p2.deck.shuffle()

        for i in range(0, opp_hand_size):
            self.p2.draw_card()


    def play_game(self):
        jump_in_phase = True
        while self.p1.life_points > 0 and self.p2.life_points > 0 and len(self.p1.deck.cards) > 0 and len(self.p2.deck.cards) > 0:
            if self.turn == self.p1:
                self.play_turn(self.turn, self.p2, jump_in_phase)
            else:
                self.play_turn(self.turn, self.p1, jump_in_phase)
            if self.p1.life_points <= 0 or self.p2.life_points <= 0:
                break
            jump_in_phase = False
            self.change_turn()
            self.turn_number += 1
        self.declare_winner()


    def play_turn(self, player, opponent, enter_from_state=False):
        if enter_from_state:
            # Entering Battle Phase direct, will be changed when state methodology changes
            bp = BattlePhase(player, opponent, is_sim=True, get_first_move=True)
            bp.execute_phase()
            self.chosen_first_move = bp.chosen_first_move

            mp2 = MainPhase2(player, is_sim=True)
            mp2.execute_phase()
        else:
            dp = DrawPhase(player, is_sim=True)
            dp.execute_phase()

            mp = MainPhase(player, is_sim=True)
            mp.execute_phase()

            if self.turn_number > 1:
                bp = BattlePhase(player, opponent, is_sim=True)
                bp.execute_phase()

            mp2 = MainPhase2(player, is_sim=True)
            mp2.execute_phase()

    def declare_winner(self):
        logging.debug("\nEnding Simulated Game\n")
        if self.p1.life_points <= 0 or len(self.p1.deck.cards) <= 0:
            self.winner = self.p2
        elif self.p2.life_points <= 0 or len(self.p2.deck.cards) <= 0:
            self.winner = self.p1






