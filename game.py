import cards
import player
import actions
import decisionmanager
import statedraw
import math
import numpy as np

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
        self.declare_winner()

    def flip_coin(self):
        return random.randint(0, 1)

    def play_turn(self, player, opponent):
        dp = DrawPhase(player)
        dp.execute_phase()

        mp = MainPhase(player)
        mp.execute_phase()

        if self.turn_number > 1:
            bp = BattlePhase(player, opponent, self.turn_number)
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
        self.turn_number += 1
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


    def ucb1(self, node_score, total_sims, edge_sims):
        c = math.sqrt(2)
        return node_score + (c * math.sqrt(np.log(total_sims)/edge_sims))


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
    def __init__(self, player, opponent, turn_number, is_sim=False, get_first_move=False, preselected_move=None):
        Phase.__init__(self, player, is_sim)
        self.opponent = opponent
        self.get_first_move = get_first_move
        self.preselected_move = preselected_move
        self.turn_number = turn_number


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
        if self.is_sim:
            logging.debug('Battle Phase Turn Number ' + str(self.turn_number))
        else:
            logging.info('Battle Phase Turn Number ' + str(self.turn_number))
        while True:
            self.player.memory.append(statedraw.write_game_state(self.player, self.opponent))
            move_list = self.get_valid_moves()
            message = str(len(move_list)) + " valid moves"
            if self.is_sim:
                logging.debug(message)
            else:
                logging.info(message)
            for mv in move_list:
                if self.is_sim:
                    logging.debug(mv.get_name())
                else:
                    logging.info(mv.get_name())

            if not self.is_sim:
                if len(move_list) > 1:
                    logging.debug('Selecting Move From ISMCTS')
                    #best_move = self.get_best_move() # Tests the game in progress
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
                if not preselected_move_located:
                    logging.debug('Preselected Move Not Found')
                    logging.debug('Preselected Move: ' + self.preselected_move.get_name())
                    for mv in move_list:
                        logging.debug('Move In List: ' + mv.get_name())
                self.preselected_move = None
            else:
                logging.debug('Rolling out for move')
                move = self.player.decisionmanager.make_decision(move_list)
            
            move.execute_move()
            if self.get_first_move:
                logging.debug('get_first_move is TRUE')
                self.chosen_first_move = move # Assigns the first chosen move to the phase to be returned for calculation of the move score
                self.post_player = copy.deepcopy(self.player)
                self.post_opponent = copy.deepcopy(self.opponent)
                self.get_first_move = False
                logging.debug('Assigning Post Player with Stats:')
                logging.debug('Post Player Name: ' + self.post_player.name)
                logging.debug('Post Opponent Name: ' + self.post_opponent.name)
                logging.debug('Post Player LP: ' + str(self.post_player.life_points))
                logging.debug('Post Opponent LP: ' + str(self.post_opponent.life_points))
            if isinstance(move, actions.AdvanceTurn):
                break
            if self.player.life_points <= 0 or self.opponent.life_points <= 0:
                break


    def get_best_move_from_ismcts(self):
        logging.info('Beginning ISMCTS Simulation')
        ismcts = self.buildISMCTS()
        i = 0
        while i < 100:
            sim_game, node, edges, move = self.select_sim_node(ismcts)
            logging.debug('Selected Node Details:')
            logging.debug(node.player.name)
            logging.debug(node.player.life_points)
            logging.debug(node.opponent.name)
            logging.debug(node.opponent.life_points)
            logging.debug(node.sims)
            logging.debug(node.wins)
            logging.debug(len(node.edges))

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
                logging.debug('Move List Not Equal')
                if move == None:
                    logging.debug('Move is none')
                else:
                    logging.debug(move.get_name())
                break

            max_score = 0
            for edge in current_node.edges:
                node_score = (edge.pre_node.wins / float(edge.pre_node.sims))
                ucb1_score = self.ucb1(node_score, edge.pre_node.sims, edge.post_node.sims)
                if ucb1_score > max_score:
                    edge_choice = edge
                    max_score = ucb1_score
                edges.append(edge_choice)
                current_node = edge_choice.post_node


        return simmed_game, current_node, edges, move


    def get_untested_move(self, game_move_list, node_move_list):
        for mv in game_move_list:
            if mv not in node_move_list:
                return mv
        return None

    '''
    def simulate_game(self):
        logging.debug("Simulating game")
        p1 = copy.deepcopy(self.player)
        p2 = copy.deepcopy(self.opponent)

        p1.set_as_sim()
        p2.set_as_sim()

        sim_game = GameInProgress(p1, p2, 2, BattlePhase)
        sim_game.play_game()
        return sim_game


    def simulate_game_for_ismcts(self, ismcts):
        logging.debug("Simulating game")
        p1 = copy.deepcopy(self.player)
        p2 = copy.deepcopy(self.opponent)

        p1.set_as_sim()
        p2.set_as_sim()

        sim_game = GameInProgress(p1, p2, 2, BattlePhase, ismcts=ismcts)
        sim_game.play_game()
        return sim_game
    '''

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


    def execute_phase(self):
        for monster in self.player.board.get_monsters():
            monster.attacked_this_turn = False


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






