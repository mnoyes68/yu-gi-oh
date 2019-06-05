import random
import math
import numpy as np
import logging

class Node():

    def __init__(self, player, opponent, turn_number, is_player_turn):
        self.player = player
        self.opponent = opponent
        self.info_set = InfoSet(player, opponent)
        self.turn_number = turn_number
        self.sims = 1
        self.wins = 0
        self.edges = []
        if is_player_turn:
            self.turn = player
        else:
            self.turn = opponent
        self.set_terminal_status()


    def set_terminal_status(self):
        if self.player.life_points == 0 or self.opponent.life_points == 0:
            self.terminal = True
        else:
            self.terminal = False


    def get_actions(self):
        actions = []
        for edge in self.edges:
            actions.append(edge.action)
        return actions


    def isLeaf(self):
        if len(self.edges) > 0:
            return False
        else:
            return True


class Edge():
    def __init__(self, pre_node, post_node, action):
        self.pre_node = pre_node
        self.post_node = post_node
        self.turn = pre_node.turn
        self.action = action


class InfoSet():
    def __init__(self, player, opponent):
        self.player_hand = player.hand
        self.player_board = player.board

        self.opponent_hand_size = opponent.hand.get_size()
        self.opponent_board = opponent.board


    def __eq__(self, other):
        if isinstance(other, InfoSet):
            return (self.player_hand == other.player_hand and 
                self.player_board == other.player_board and 
                self.opponent_hand_size == other.opponent_hand_size and 
                self.opponent_board == other.self.opponent_board)
        return False


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        player_hand_ids = (o.card_id for o in self.player_hand.get_cards()).sort()
        player_board_ids = (o.card_id for o in self.player_board.get_monsters()).sort()
        player_grave_ids = (o.card_id for o in self.player_board.graveyard.get_cards()).sort()

        opponent_board_ids = (o.card_id for o in self.opponent_board.get_monsters()).sort()
        opponent_grave_ids = (o.card_id for o in self.opponent_board.graveyard.get_cards()).sort()

        return hash(str(player_hand_ids) + ":" + 
            str(player_board_ids) + ":" + 
            str(player_grave_ids) + ":" + 
            str(self.opponent_hand_size) + ":" + 
            str(opponent_board_ids) + ":" + 
            str(opponent_grave_ids))
        

class ISMCTS():

    def __init__(self, root):
        self.root = root
        self.tree = set()
        self.add_node(root)
    

    def __len__(self):
        return len(self.tree)


    def add_node(self, node):
        self.tree.add(node)


    def select_sim_node(self):
        current_node = self.root
        edges = []
        logging.debug('Traversing ISMCTS')
        while not current_node.isLeaf():
            #edge_choice = random.choice(current_node.edges)
            max_score = 0
            for edge in current_node.edges:
                node_score = (edge.pre_node.wins / float(edge.pre_node.sims))
                ucb1_score = self.ucb1(node_score, edge.pre_node.sims, edge.post_node.sims)
                if ucb1_score > max_score:
                    edge_choice = edge
                    max_score = ucb1_score
                edges.append(edge_choice)
                current_node = edge_choice.post_node
        return current_node, edges


    def expand(self, pre_node, player, opponent, action, turn_number, is_player_turn):
        post_node = Node(player, opponent, turn_number, is_player_turn)
        edge = Edge(pre_node, post_node, action)
        pre_node.edges.append(edge)
        self.tree.add(post_node)


    def back_propogate(self, node, edges, player_wins):
        current_node = node
        while current_node != None:
            current_node.sims += 1
            if player_wins:
                current_node.wins += 1
            if not edges:
                current_node = None
            else:
                edge = edges.pop(-1)
                current_node = edge.pre_node


    def ucb1(self, node_score, total_sims, edge_sims):
        c = math.sqrt(2)
        return node_score + (c * math.sqrt(np.log(total_sims)/edge_sims))


