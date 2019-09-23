import cards
import player
import actions
import decisionmanager
import statedraw
import math
import json
import numpy as np
import pdb

from pandas.io.json import json_normalize
from timeit import default_timer as timer
from ISMCTS import Node, Edge, InfoSet, ISMCTS
from sklearn import preprocessing

from keras.models import Sequential
from keras.layers import Activation
from keras.layers import BatchNormalization
from keras.layers import Dense
from keras.layers import Flatten
from keras import regularizers

import copy
import random
import operator
import logging

class Game():
    def __init__(self, p1, p2, rollout=False, is_sim=False, turn_number=1, entry_phase=None, preselected_first_move=None, shuffle_unknown_cards=False):
        self.p1 = p1
        self.p2 = p2
        self.turn_number = turn_number
        self.winner = None
        self.rollout = rollout
        self.is_sim = is_sim
        self.game_is_over = False
        self.game_has_begun = False
        self.save_first_move = False
        self.preselected_first_move = preselected_first_move
        self.model = None
        self.scaler = None

        if shuffle_unknown_cards:
            self.shuffle_unknown_cards()

        if self.is_sim:
            self.turn = self.p1
            self.begin_phase = entry_phase
            self.save_first_move = True
            self.initialize_sim_game()
        else:
            self.model = self.create_model_structure()
            self.scaler = self.create_scaler()


    def create_model_structure(self):
        model = Sequential()
        model.add(Dense(100, input_dim=59, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
        model.add(BatchNormalization())
        model.add(Dense(50, activation="relu", kernel_regularizer=regularizers.l2(0.0002)))
        model.add(BatchNormalization())
        model.add(Dense(1, activation="sigmoid"))
        model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
        model.load_weights("model.h5")
        return model


    def create_scaler(self):
        scaler = preprocessing.MinMaxScaler()
        with open('training_data.json') as f:
            data = json.load(f)
            dfx = json_normalize(data)
        scaler.fit(dfx)
        return scaler


    def play_game(self):
        if self.game_is_over:
            self.declare_winner()
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
            self.declare_winner()
            return False
        phase_continue = self.current_phase.execute_step()
        self.preselected_first_move = None

        if self.save_first_move:
            self.chosen_first_move = self.current_phase.chosen_first_move
            self.post_player = self.current_phase.post_player
            self.post_opponent = self.current_phase.post_opponent
            self.save_first_move = False

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


    def get_valid_moves(self):
        return self.current_phase.get_valid_moves()


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
        phase_list.append(DrawPhase(player, rollout=self.rollout, is_sim=self.is_sim, preselected_move=self.preselected_first_move))
        phase_list.append(MainPhase(player, rollout=self.rollout, is_sim=self.is_sim, preselected_move=self.preselected_first_move))
        if self.turn_number > 1:
            phase_list.append(BattlePhase(player, opponent, self.turn_number, self.model, self.scaler, rollout=self.rollout, is_sim=self.is_sim, preselected_move=self.preselected_first_move))
        phase_list.append(MainPhase2(player, rollout=self.rollout, is_sim=self.is_sim, preselected_move=self.preselected_first_move))
        return phase_list


    def get_begin_phase(self):
        for phase in self.phase_list:
            if isinstance(phase, self.begin_phase):
                return phase
        return None


    def initialize_game(self):
        for i in range (0,5):
            self.p1.draw_card()
            self.p2.draw_card()
        self.begin_game()


    def initialize_sim_game(self):
        self.phase_list = self.get_phase_list(self.turn, self.get_opponent())
        self.current_phase = self.get_begin_phase()
        self.current_phase.get_first_move = self.save_first_move
        self.game_has_begun = True


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
        self.log_sim(self.p1.name + " " + str(self.p1.life_points))
        self.log_sim(self.p1.name + " " + str(self.p1.deck.cards))
        self.log_sim(self.p2.name + " " + str(self.p2.life_points))
        self.log_sim(self.p2.name + " " + str(self.p2.deck.cards))
        if self.p1.life_points <= 0 or len(self.p1.deck.cards) <= 0:
            self.winner = self.p2
        elif self.p2.life_points <= 0 or len(self.p2.deck.cards) <= 0:
            self.winner = self.p1


    def log_sim(self, message):
        if self.is_sim:
            logging.debug(message)
        else:
            logging.info(message)


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


class Phase():
    def __init__(self, player, rollout=False, is_sim=False, get_first_move=False, preselected_move=None):
        self.player = player
        self.rollout = rollout
        self.is_sim = is_sim
        self.get_first_move = get_first_move
        self.preselected_move = preselected_move


    def execute_phase(self):
        phase_ongoing = True
        while phase_ongoing:
            phase_ongoing = self.execute_step()


    def execute_step(self):
        raise NotImplementedError('users must define to use this base class')


    def get_valid_moves(self):
        raise NotImplementedError('users must define to use this base class')


    def get_corresponding_action(self, external_move):
        for move in self.get_valid_moves():
            if move == external_move:
                return move
        return None


    def run_simulation(self, ismcts):
        return ismcts


    def ucb1(self, node_score, total_sims, edge_sims):
        c = math.sqrt(2)
        return node_score + (c * math.sqrt(np.log(total_sims)/edge_sims))


    def log_sim(self, message):
        if self.is_sim:
            logging.debug(message)
        else:
            logging.info(message)


class DrawPhase(Phase):
    def __init__(self, player, rollout=False, is_sim=False, get_first_move=False, preselected_move=None):
        Phase.__init__(self, player, rollout=rollout, is_sim=is_sim, get_first_move=get_first_move, preselected_move=preselected_move)


    def get_valid_moves(self):
        move_list = []
        move_list.append(actions.DrawCard(self.player))
        return move_list


    def execute_step(self):
        self.player.draw_card()
        return False


class MainPhase(Phase):
    def __init__(self, player, rollout=False, is_sim=False, get_first_move=False, preselected_move=None):
        Phase.__init__(self, player, rollout=rollout, is_sim=is_sim, get_first_move=get_first_move, preselected_move=preselected_move)


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
    def __init__(self, player, opponent, turn_number, model, scaler, rollout=False, is_sim=False, get_first_move=False, preselected_move=None):
        Phase.__init__(self, player, rollout=rollout, is_sim=is_sim, get_first_move=get_first_move, preselected_move=preselected_move)
        self.opponent = opponent
        self.turn_number = turn_number
        self.model = model
        self.scaler = scaler


    def enter_ismcts_debug(self):
        move_list = self.get_valid_moves()


    def execute_step(self):
        self.player.memory.append(statedraw.write_game_state(self.player, self.opponent))
        move_list = self.get_valid_moves()
        self.log_sim(str(len(move_list)) + " valid moves")
        for mv in move_list:
            self.log_sim(mv.get_name())

        if self.rollout:
            logging.debug('Rolling out for move')
            move = self.player.decisionmanager.make_decision(move_list)
        elif not self.is_sim:
            if len(move_list) > 1:
                #best_move = self.get_best_move_from_ismcts() # Tests the game in progress
                best_move = self.get_best_move_from_full_model(self.model, self.scaler)
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
        logging.debug('Beginning ISMCTS Simulation')
        ismcts = self.buildISMCTS()
        i = 0
        while i < 400:
            logging.debug('Simulation ' + str(i+1))
            ismcts = self.run_simulation(ismcts)
            i += 1
        logging.debug('Ending ISMCTS Simulation')

        max_score = 0
        best_move = None
        for edge in ismcts.root.edges:
            score = edge.post_node.wins/float(edge.post_node.sims)
            logging.info(edge.action.get_name() + " " + str(edge.post_node.wins) + "/" + str(edge.post_node.sims) + " , " + str(score))
            if score > max_score or best_move == None:
                max_score = score
                best_move = edge.action
        return best_move


    def get_best_move_from_full_model(self, model, scaler):
        #logging.info('Beginning Full Model Simulation')
        ismcts = self.buildISMCTS()
        i = 0
        while i < 400:
            logging.debug('Simulation ' + str(i+1))
            ismcts = self.run_simulation(ismcts)
            i += 1
        #logging.info('Ending Full Model Simulation')

        max_score = 0
        best_move = None
        for edge in ismcts.root.edges:
            logging.info("Analyzing " + edge.action.get_name())
            ismcts_score = edge.post_node.wins/float(edge.post_node.sims)
            post_state = statedraw.write_game_state(edge.post_node.player, edge.post_node.opponent)
            post_state['ID'] = 1

            logging.info(post_state)

            dfx = json_normalize([post_state])
            X = scaler.transform(dfx)
            network_score = model.predict(X)[0][0]
            #logging.info('ISMCTS Score: ' + str(ismcts_score))
            #logging.info('Network Score: ' + str(network_score))
            #score = (ismcts_score + network_score) / 2
            score = network_score
            #logging.info(edge.action.get_name() + " " + str(edge.post_node.wins) + "/" + str(edge.post_node.sims) + " , " + str(score))
            logging.info(edge.action.get_name() + " , " + str(score))
            if score > max_score or best_move == None:
                max_score = score
                best_move = edge.action
        return best_move


    def run_simulation(self, ismcts):
        sim_game, node, edges, move = self.select_sim_node(ismcts)
        sim_game.play_step()
        if sim_game.turn.name == self.player.name:
            is_player_turn = True
        else:
            is_player_turn = False

        sim_game.play_game()
        winner = sim_game.winner
        if not node.terminal:
            post_player = sim_game.post_player
            post_opponent = sim_game.post_opponent
            edge, post_node = ismcts.expand(node, post_player, post_opponent, move, sim_game.turn_number, is_player_turn)
            edges.append(edge)
        else:
            post_node = node

        if winner.name == self.player.name:
            ismcts.back_propogate(post_node, edges, True)
        else:
            ismcts.back_propogate(post_node, edges, False)
        return ismcts


    def select_sim_node(self, ismcts):
        current_node = ismcts.root
        edges = []
        simmed_game = self.create_simmed_game(current_node.player, current_node.opponent, 2, BattlePhase, None)
        i = 0
        while True:
            game_move_list = simmed_game.get_valid_moves()
            node_move_list = current_node.get_actions()
            move = self.get_untested_move(game_move_list, node_move_list)
            if move:
                simmed_game.current_phase.preselected_move = move
                break
            max_score = 0
            edge_choice = None
            for edge in current_node.edges:
                if simmed_game.turn.name == self.player.name:
                    node_score = (edge.post_node.wins / float(edge.post_node.sims))
                else:
                    losses = edge.post_node.sims - edge.post_node.wins
                    node_score = (losses / float(edge.post_node.sims))
                ucb1_score = self.ucb1(node_score, edge.pre_node.sims, edge.post_node.sims)
                if ucb1_score > max_score or edge_choice == None:
                    edge_choice = edge
                    max_score = ucb1_score

            edges.append(edge_choice)
            current_node = edge_choice.post_node
            simmed_game.current_phase.preselected_move = self.get_corresponding_action(edge_choice.action)
            simmed_game.play_step()
            i += 1

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


    def create_simmed_game(self, player, opponent, turn_number, phase, move):
        p1 = copy.deepcopy(player)
        p2 = copy.deepcopy(opponent)

        p1.set_as_sim()
        p2.set_as_sim()

        sim_game = Game(p1, p2, is_sim=True, turn_number=turn_number, entry_phase=phase, preselected_first_move=move, shuffle_unknown_cards=True)
        return sim_game


    def buildISMCTS(self):
        root_node = Node(self.player, self.opponent, self.turn_number, True)
        return ISMCTS(root_node)


class MainPhase2(Phase):
    def __init__(self, player, rollout=False, is_sim=False, get_first_move=False, preselected_move=None):
        Phase.__init__(self, player, rollout=rollout, is_sim=is_sim, get_first_move=get_first_move, preselected_move=preselected_move)


    def get_valid_moves(self):
        move_list = []
        move_list.append(actions.AdvanceTurn(is_sim=self.is_sim))
        return move_list


    def execute_step(self):
        for monster in self.player.board.get_monsters():
            monster.attacked_this_turn = False
        return False





