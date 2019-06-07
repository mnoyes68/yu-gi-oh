import cards
import player
import actions
import decisionmanager
import statedraw
import math
import numpy as np
import pdb

from ISMCTS import Node, Edge, InfoSet, ISMCTS

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
        self.game_is_over = False
        self.game_has_begun = False


    def play_game(self):
        if self.game_is_over:
            return

        if not self.game_has_begun:
            self.initialize_game()

        while not self.game_is_over:
            self.play_turn(self.turn, self.get_opponent())

        self.declare_winner()


    def play_turn(self, player, opponent):
        if self.is_game_over():
            return False

        turn_in_progress = True
        while turn_in_progress:
            turn_in_progress = self.play_phase()

        if self.game_is_over:
            return False
        return True


    def play_phase(self):
        if self.is_game_over():
            return False

        phase_in_progress = True
        while phase_in_progress:
            phase_in_progress = self.play_step()
        if self.is_game_over():
            return False


    def play_step(self):
        if self.is_game_over():
            return False
        phase_continue = self.current_phase.execute_step()
        if not phase_continue:
            if self.is_game_over():
                return False
            self.change_phase()


    def change_phase(self):
        phase_index = self.phase_list.index(self.current_phase) + 1
        if phase_index == len(self.phase_list):
            self.change_turn()
            return False
        else:
            self.current_phase = self.phase_list[phase_index]

        return True


    def change_turn(self):
        if self.turn == self.p1:
            self.turn = self.p2
        else:
            self.turn = self.p1
        self.turn_number += 1
        self.log_sim("It is now " + self.turn.name + "'s Turn")
        self.phase_list = self.get_phase_list(self.turn, self.get_opponent())
        self.current_phase = self.phase_list[0]


    def flip_coin(self):
        return random.randint(0, 1)


    def is_game_over(self):
        if self.p1.life_points <= 0 or self.p2.life_points <= 0:
            self.game_is_over = True
        return self.game_is_over


    def get_opponent(self):
        if self.turn == self.p1:
            return self.p2
        else:
            return self.p1


    def get_player(self):
        if self.turn == self.p1:
            return self.p1
        else:
            return self.p2


    def get_phase_list(self, player, opponent):
        phase_list = []
        phase_list.append(DrawPhase(player))
        phase_list.append(MainPhase(player))
        if self.turn_number > 1:
            phase_list.append(BattlePhase(player, opponent, self.turn_number))
        phase_list.append(MainPhase2(player))
        return phase_list


    def initialize_game(self):
        for i in range (0,5):
            self.p1.draw_card()
            self.p2.draw_card()
        self.begin_game()


    def begin_game(self):
        logging.info('\n' + "BEGIN GAME!!!" + '\n')
        coin_flip = self.flip_coin()
        if coin_flip == 0:
            self.turn = self.p1 
        else:
            self.turn = self.p2
        logging.info(self.turn.name + " goes first")
        self.phase_list = self.get_phase_list(self.turn, self.get_opponent())
        self.current_phase = self.phase_list[0]
        self.game_has_begun = True


    def declare_winner(self):
        if self.p1.life_points <= 0 or len(self.p1.deck.cards) <= 0:
            self.winner = self.p2
        elif self.p2.life_points <= 0 or len(self.p2.deck.cards) <= 0:
            self.winner = self.p1


    def log_sim(self, message):
        if self.is_sim:
            logging.debug(message)
        else:
            logging.info(message)


class Phase():
    def __init__(self, player, is_sim=False):
        self.player = player
        self.is_sim = is_sim


    def execute_phase(self):
        phase_ongoing = True
        while phase_ongoing:
            phase_ongoing = self.execute_step()


    def execute_step(self):
        raise NotImplementedError('users must define execute to use this base class')


    def ucb1(self, node_score, total_sims, edge_sims):
        c = math.sqrt(2)
        return node_score + (c * math.sqrt(np.log(total_sims)/edge_sims))


    def log_sim(self, message):
        if self.is_sim:
            logging.debug(message)
        else:
            logging.info(message)


class DrawPhase(Phase):
    def __init__(self, player, is_sim=False):
        Phase.__init__(self, player, is_sim)


    def execute_step(self):
        self.player.draw_card()
        return False


class MainPhase(Phase):
    def __init__(self, player, is_sim=False):
        Phase.__init__(self, player, is_sim)


    def get_valid_moves(self):
        move_list = []
        move_list.append(actions.AdvanceTurn())
        for card in self.player.hand.get_cards():
            if isinstance(card, cards.MonsterCard):
                move = actions.NormalSummon(self.player, card)
                move_list.append(move)
        return move_list


    def execute_step(self):
        card_choice = self.player.decisionmanager.make_decision(self.player.hand.cards)
        move = actions.NormalSummon(self.player, card_choice, is_sim=self.is_sim)
        move.execute_move()
        return False


class BattlePhase(Phase):
    def __init__(self, player, opponent, turn_number, is_sim=False, get_first_move=False, preselected_move=None):
        Phase.__init__(self, player, is_sim)
        self.opponent = opponent
        self.get_first_move = get_first_move
        self.preselected_move = preselected_move
        self.turn_number = turn_number


    def execute_step(self):
        self.player.memory.append(statedraw.write_game_state(self.player, self.opponent))
        move_list = self.get_valid_moves()
        self.log_sim(str(len(move_list)) + " valid moves")
        for mv in move_list:
            self.log_sim(mv.get_name())

        if not self.is_sim:
            if len(move_list) > 1:
                best_move = self.get_best_move_from_ismcts() # Tests the game in progress
                logging.debug('Selected best move: ' + best_move.get_name())
                for mv in move_list:
                    logging.debug('Comparing against: ' + mv.get_name())
                    if best_move == mv:
                        logging.debug('Match Obtained')
                        move = mv
                        break
            else:
                logging.debug('Single move available')
                move = move_list[0]
        elif self.preselected_move != None:
            logging.debug('Using Preselected Move')
            preselected_move_located = False
            for mv in move_list:
                if self.preselected_move == mv:
                    move = mv
                    preselected_move_located = True
                    break
            self.preselected_move = None
        else:
            logging.debug('Rolling out for move')
            move = self.player.decisionmanager.make_decision(move_list)
        
        move.execute_move()
        if self.get_first_move:
            self.set_post_state(move)
            self.get_first_move = False
        if isinstance(move, actions.AdvanceTurn):
            return False
        if self.player.life_points <= 0 or self.opponent.life_points <= 0:
            return False
        return True


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


    def get_best_move_from_ismcts(self):
        logging.info('Beginning ISMCTS Simulation')
        ismcts = self.buildISMCTS()
        i = 0
        while i < 100:
            sim_game, node, edges, move = self.select_sim_node(ismcts)

            if node.player == self.player:
                is_player_turn = True
            else:
                is_player_turn = False

            sim_game.play_game()
            winner = sim_game.winner
            if not node.terminal:
                logging.debug('Selecting post_player')
                post_player = sim_game.post_player
                post_opponent = sim_game.post_opponent
                if isinstance(move, actions.AdvanceTurn):
                    is_player_turn = not is_player_turn
                    turn_number = node.turn_number + 1
                else:
                    is_player_turn = is_player_turn
                    turn_number = node.turn_number
                
                logging.debug('Expanding Node With Details:')
                logging.debug(post_player.name)
                logging.debug(post_player.life_points)
                logging.debug(post_opponent.name)
                logging.debug(post_opponent.life_points)
                ismcts.expand(node, post_player, post_opponent, move, turn_number, is_player_turn)
            if winner.name == self.player.name:
                ismcts.back_propogate(node, edges, True)
            else:
                ismcts.back_propogate(node, edges, False)
            i += 1
            logging.debug('i is now ' + str(i))
        logging.info('Ending ISMCTS Simulation')

        max_score = 0
        best_move = None
        for edge in ismcts.root.edges:
            score = edge.post_node.wins/float(edge.post_node.sims)
            logging.info(edge.action.get_name() + " " + str(edge.post_node.wins) + "/" + str(edge.post_node.sims) + " , " + str(score))
            if score > max_score or best_move == None:
                max_score = score
                best_move = edge.action
        return best_move


    def select_sim_node(self, ismcts):
        current_node = ismcts.root
        edges = []
        logging.debug('Traversing ISMCTS')
        while True:
            #pdb.set_trace()
            simmed_game = self.simulate_game_with_arg_players(current_node.player, current_node.opponent, 2, BattlePhase, None)
            game_move_list = simmed_game.get_available_moves()
            node_move_list = current_node.get_actions()
            logging.debug('Game Move List: Length ' + str(len(game_move_list)))
            for mv in game_move_list:
                logging.debug(mv.get_name())
            logging.debug('Node Move List: Length ' + str(len(node_move_list)))
            for mv in node_move_list:
                if not mv:
                    logging.debug('Move is none')
                else:
                    logging.debug(mv.get_name())
            move = self.get_untested_move(game_move_list, node_move_list)
            if move:
                logging.debug('Selected untested move: ' + move.get_name())
                break

            max_score = 0
            edge_choice = None
            logging.debug('Scoring edges')
            for edge in current_node.edges:
                node_score = (edge.pre_node.wins / float(edge.pre_node.sims))
                ucb1_score = self.ucb1(node_score, edge.pre_node.sims, edge.post_node.sims)
                logging.debug(edge.action.get_name() + " - Node: " + str(node_score) + " UCB1: " + str(ucb1_score))
                if ucb1_score > max_score or edge_choice == None:
                    edge_choice = edge
                    max_score = ucb1_score
                edges.append(edge_choice)
                current_node = edge_choice.post_node

            logging.debug('Moving to state with action: ' + edge_choice.action.get_name())

        return simmed_game, current_node, edges, move


    def set_post_state(self, move):
        self.chosen_first_move = move # Assigns the first chosen move to the phase to be returned for calculation of the move score
        self.post_player = copy.deepcopy(self.player)
        self.post_opponent = copy.deepcopy(self.opponent)


    def get_untested_move(self, game_move_list, node_move_list):
        for mv in game_move_list:
            if mv not in node_move_list:
                return mv
        return None


    def simulate_game_with_arg_players(self, player, opponent, turn_number, phase, move):
        logging.debug("Creating simulated game")
        p1 = copy.deepcopy(player)
        p2 = copy.deepcopy(opponent)

        p1.set_as_sim()
        p2.set_as_sim()

        sim_game = GameInProgress(p1, p2, turn_number, phase, preselected_first_move=move)
        logging.debug("Simulated game created")
        return sim_game


    def buildISMCTS(self):
        root_node = Node(self.player, self.opponent, self.turn_number, True)
        return ISMCTS(root_node)


class MainPhase2(Phase):
    def __init__(self, player, is_sim=False):
        Phase.__init__(self, player, is_sim)


    def execute_step(self):
        for monster in self.player.board.get_monsters():
            monster.attacked_this_turn = False
        return False


class GameInProgress(Game):
    def __init__(self, player, opponent, turn_number, phase, shuffle_unknown_cards=True, preselected_first_move=None):
        Game.__init__(self, player, opponent)
        self.turn_number = turn_number
        self.turn = player
        self.begin_phase = phase
        self.is_sim = True
        self.preselected_first_move = preselected_first_move
        if shuffle_unknown_cards:
            self.shuffle_unknown_cards()


    def shuffle_unknown_cards(self):
        opp_hand_size = self.p2.hand.get_size()
        logging.debug("Opponent Hand Size: " + str(opp_hand_size))

        logging.debug("Deck size before return: " + str(self.p2.deck.get_size()))
        opp_hand_cards = self.p2.hand.get_cards()
        for c in opp_hand_cards:
            logging.debug(c.name)
        logging.debug('Returning Cards')
        self.p2.add_cards_to_deck()
        logging.debug("Deck size after return: " + str(self.p2.deck.get_size()))

        self.p1.deck.shuffle()
        self.p2.deck.shuffle()

        for i in range(0, opp_hand_size):
            self.p2.draw_card()


    def play_game(self):
        jump_in_phase = True
        logging.debug('Jumping into phase with stats')
        logging.debug('Turn Number: ' + str(self.turn_number))
        logging.debug('P1 Life Points: ' + str(self.p1.life_points))
        logging.debug('P2 Life Points: ' + str(self.p2.life_points))
        if self.preselected_first_move:
            logging.debug('Chosen First Move: ' + self.preselected_first_move.get_name())
        else:
            logging.debug('No Chosen First Move')
        while self.p1.life_points > 0 and self.p2.life_points > 0 and len(self.p1.deck.cards) > 0 and len(self.p2.deck.cards) > 0:
            if self.turn == self.p1:
                self.play_turn(self.turn, self.p2, jump_in_phase)
            else:
                self.play_turn(self.turn, self.p1, jump_in_phase)
            if self.p1.life_points <= 0 or self.p2.life_points <= 0:
                break
            jump_in_phase = False
            self.change_turn()
        self.declare_winner()


    def play_turn(self, player, opponent, enter_from_state=False):
        if enter_from_state:
            logging.debug('Playing Sim Turn and entering from state')
            # Entering Battle Phase direct, will be changed when state methodology changes
            bp = BattlePhase(player, opponent, self.turn_number, is_sim=True, get_first_move=True, preselected_move=self.preselected_first_move)
            bp.execute_phase()
            self.chosen_first_move = bp.chosen_first_move
            self.post_player = bp.post_player
            self.post_opponent = bp.post_opponent

            mp2 = MainPhase2(player, is_sim=True)
            mp2.execute_phase()
        else:
            dp = DrawPhase(player, is_sim=True)
            dp.execute_phase()

            mp = MainPhase(player, is_sim=True)
            mp.execute_phase()

            if self.turn_number > 1:
                bp = BattlePhase(player, opponent, self.turn_number, is_sim=True)
                bp.execute_phase()

            mp2 = MainPhase2(player, is_sim=True)
            mp2.execute_phase()


    def get_available_moves(self):
        bp = BattlePhase(self.p1, self.p2, self.turn_number, is_sim=True, get_first_move=True, preselected_move=self.preselected_first_move)
        return bp.get_valid_moves()


    def declare_winner(self):
        logging.debug("Ending Simulated Game\n")
        logging.debug(self.p1.life_points)
        logging.debug(len(self.p1.deck.cards))
        logging.debug(self.p2.life_points)
        logging.debug(len(self.p2.deck.cards))
        if self.p1.life_points <= 0 or len(self.p1.deck.cards) <= 0:
            self.winner = self.p2
        elif self.p2.life_points <= 0 or len(self.p2.deck.cards) <= 0:
            self.winner = self.p1






