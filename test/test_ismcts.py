import sys
import os
import logging
import json
import pytest
import random

sys.path.append(os.path.join(os.path.abspath("."), "yugioh"))

from ISMCTS import Node, ISMCTS
import cards
import player
import game
import actions
import statedraw

from pandas.io.json import json_normalize

def create_and_launch_game():
    logging.basicConfig(filename='ismcts.log', level=logging.INFO, filemode='w')
    with open("decks/yugi.json", "r") as deck:
        deck_json = json.loads(deck.read())
        ygogame = create_training_game(deck_json)
        ygogame.initialize_game()
        return ygogame


def create_deck(json):
    deck_list = []
    for c in json:
        card = cards.MonsterCard(c.get('name'), c.get('id'), c.get('atk'), c.get('defn'), c.get('level'))
        deck_list.append(card)
    deck = cards.Deck(deck_list, shuffle=False)
    return deck


def create_training_game(deck_json):
    yugi_deck = create_deck(deck_json)
    opp_deck = create_deck(deck_json)

    yugi = player.ComputerPlayer("Yugi", yugi_deck, None)
    opponent = player.ComputerPlayer("Opponent", opp_deck, None)

    ygogame = game.Game(yugi, opponent)
    return ygogame


@pytest.mark.skip()
def test_game_ismcts_begin():
    ygogame = create_and_launch_game()
    while not isinstance(ygogame.current_phase, game.BattlePhase):
        ygogame.play_phase()

    tree = ygogame.current_phase.buildISMCTS()
    assert tree.root.player.life_points == 4000


@pytest.mark.skip()
def test_properly_traverse_old():
    ygogame = create_and_launch_game()
    while not isinstance(ygogame.current_phase, game.BattlePhase):
        ygogame.play_phase()

    ismcts = ygogame.current_phase.buildISMCTS()
    ismcts = ygogame.current_phase.run_simulation(ismcts)
    ismcts = ygogame.current_phase.run_simulation(ismcts) 
    assert len(ismcts.root.edges) == 2

    for i in range(20):
        ismcts = ygogame.current_phase.run_simulation(ismcts)
    assert len(ismcts.root.edges) == 2


def test_properly_traverse():
    test_count = 0
    valid_test_count = 0
    should_adv_count = 0
    should_atk_count = 0
    success_count = 0
    equal_count = 0

    for i in range(20):
        ygogame = create_and_launch_game()
        while not isinstance(ygogame.current_phase, game.BattlePhase):
            ygogame.play_phase()

        ismcts = ygogame.current_phase.buildISMCTS()
        for i in range(400):
            ismcts = ygogame.current_phase.run_simulation(ismcts)

        # Score Simulation
        adv_visit_score = 0
        adv_win_score = 0
        atk_visit_score = 0
        atk_win_score = 0
        should_atk = False
        equal = False

        for edge in ismcts.root.edges:
            print edge.action.get_name()
            print edge.post_node.wins , "/", edge.post_node.sims
            if isinstance(edge.action, actions.Attack):
                monst_atk = edge.action.monster.atk
                target_atk = edge.action.target.atk
                if monst_atk > target_atk:
                    should_atk = True
                elif monst_atk == target_atk:
                    equal = True
                atk_visit_score = edge.post_node.sims
                atk_win_score = edge.post_node.wins
            elif isinstance(edge.action, actions.AdvanceTurn):
                adv_visit_score = edge.post_node.sims
                adv_win_score = edge.post_node.wins

        test_count += 1
        if equal:
            equal_count += 1
        elif should_atk:
            valid_test_count += 1
            should_atk_count += 1
            if atk_visit_score > adv_visit_score:
                success_count += 1
        else:
            valid_test_count += 1
            should_adv_count += 1
            if adv_visit_score > atk_visit_score:
                success_count += 1

        print ""

    print 'Test Score:', success_count/float(valid_test_count)
    print 'Test Count:', test_count
    print 'Valid Test Count:', valid_test_count
    print 'Success Count:', success_count
    print 'Should Advance Count:', should_adv_count
    print 'Should Attack Count:', should_atk_count
    print 'Equal Count:', equal_count


@pytest.mark.skip()
def test_run_single_ismcts_sim():
    ygogame = create_and_launch_game()
    while not isinstance(ygogame.current_phase, game.BattlePhase):
        ygogame.play_phase()

    ismcts = ygogame.current_phase.buildISMCTS()
    ismcts = ygogame.current_phase.run_simulation(ismcts)
    ismcts = ygogame.current_phase.run_simulation(ismcts) 

    sim_game, node, edges, move = ygogame.current_phase.select_sim_node(ismcts)
    print edges[0].action.get_name()
    print move.get_name()
    print sim_game.current_phase

    ismcts = ygogame.current_phase.run_simulation(ismcts)
    sim_game, node, edges, move = ygogame.current_phase.select_sim_node(ismcts)
    print edges[0].action.get_name()
    print move.get_name()
    print sim_game.current_phase


def test_custom_ismcts():
    ygogame = create_and_launch_game()
    yugi = ygogame.p1
    opponent = ygogame.p2

    node = Node(yugi, opponent, 1, True)
    tree = ISMCTS(node)

    node.player.life_points 
    assert tree.root.player.life_points == 4000
    assert opponent.life_points == 4000


def test_select_sim_node():
    ygogame = create_and_launch_game()
    while not isinstance(ygogame.current_phase, game.BattlePhase):
        ygogame.play_phase()

    ismcts = ygogame.current_phase.buildISMCTS()
    sim_game, node, edges, move = ygogame.current_phase.select_sim_node(ismcts)
    assert isinstance(move, actions.AdvanceTurn)
    ismcts = ygogame.current_phase.run_simulation(ismcts)

    sim_game, node, edges, move = ygogame.current_phase.select_sim_node(ismcts)
    assert isinstance(move, actions.Attack)
    ismcts = ygogame.current_phase.run_simulation(ismcts)

    '''
    ismcts = ygogame.current_phase.buildISMCTS()
    ismcts = ygogame.current_phase.run_simulation(ismcts)
    ismcts = ygogame.current_phase.run_simulation(ismcts) 
    assert len(ismcts.root.edges) == 2

    for i in range(20):
        ismcts = ygogame.current_phase.run_simulation(ismcts)
    assert len(ismcts.root.edges) == 2
    '''


def select_sim_node(phase, ismcts):
    current_node = ismcts.root
    edges = []
    simmed_game = phase.create_simmed_game(current_node.player, current_node.opponent, 2, game.BattlePhase, None)
    i = 0
    while True:
        print 'Current Node Score:', current_node.wins, '/', current_node.sims
        game_move_list = simmed_game.get_valid_moves()
        node_move_list = current_node.get_actions()
        move = phase.get_untested_move(game_move_list, node_move_list)
        if move:
            simmed_game.current_phase.preselected_move = move
            break
        max_score = 0
        edge_choice = None
        for edge in current_node.edges:
            if simmed_game.turn.name == phase.player.name:
                node_score = (edge.post_node.wins / float(edge.post_node.sims))
            else:
                losses = edge.post_node.sims - edge.post_node.wins
                node_score = (losses / float(edge.post_node.sims))
            ucb1_score = phase.ucb1(node_score, edge.pre_node.sims, edge.post_node.sims)
            if ucb1_score > max_score or edge_choice == None:
                edge_choice = edge
                max_score = ucb1_score

        print 'Chosen Edge Action:', edge_choice.action.get_name()
        edges.append(edge_choice)
        current_node = edge_choice.post_node
        simmed_game.current_phase.preselected_move = phase.get_corresponding_action(edge_choice.action)
        simmed_game.play_step()
        i += 1


    return simmed_game, current_node, edges, move


def run_simulation(phase, ismcts):
    sim_game, node, edges, move = select_sim_node_surgically(phase, ismcts)
    print('Chosen Move: ' + move.get_name())
    print('Sim Game Phase: '  + sim_game.current_phase.__class__.__name__)
    print('Node Player: ' + node.player.name)
    print('Node Opponent: ' + node.opponent.name)
    print('Node Turn Name: ' + node.turn.name)
    print('Simmed Game Turn Name: ' + sim_game.turn.name)

    print 'Stepping Game'
    sim_game.play_step()
    if sim_game.turn.name == phase.player.name:
        is_player_turn = True
    else:
        is_player_turn = False
    print 'Is Player Turn:', is_player_turn

    print 'Playing Sim Game'
    sim_game.play_game()
    winner = sim_game.winner
    print 'Winner:', winner.name
    if not node.terminal:
        post_player = sim_game.post_player
        post_opponent = sim_game.post_opponent
        edge, post_node = ismcts.expand(node, post_player, post_opponent, move, sim_game.turn_number, is_player_turn)
        print('Expanded Edge Move: ' + edge.action.get_name())
        edges.append(edge)
    else:
        post_node = node

    if winner.name == phase.player.name:
        ismcts.back_propogate(post_node, edges, True)
    else:
        ismcts.back_propogate(post_node, edges, False)
    return ismcts


def find_advance_turn(edges):
    for edge in edges:
        if isinstance(edge.action, actions.AdvanceTurn):
            return edge
    return None


def test_expand():
    random.seed(60)
    ygogame = create_and_launch_game()
    while not isinstance(ygogame.current_phase, game.BattlePhase):
        ygogame.play_phase()

    ismcts = ygogame.current_phase.buildISMCTS()
    i = 0
    while i < 10:
        print('')
        print('Simulation ' + str(i+1))
        run_simulation_surgically(ygogame.current_phase, ismcts)
        edge = find_advance_turn(ismcts.root.edges)
        post_state = statedraw.write_game_state(edge.post_node.player, edge.post_node.opponent)
        #print(post_state)
        i += 1

    print('Edges Length: ' + str(len(ismcts.root.edges)))

    '''
    for edge in ismcts.root.edges:
        print("Analyzing " + edge.action.get_name())

        post_state = statedraw.write_game_state(edge.post_node.player, edge.post_node.opponent)
        post_state['ID'] = 1
        print(post_state)
        
        dfx = json_normalize([post_state])
        X = ygogame.scaler.transform(dfx)
        network_score = ygogame.model.predict(X)[0][0]
        score = network_score
        print(edge.action.get_name() + " , " + str(score))
    '''


    '''
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



    ismcts = ygogame.current_phase.buildISMCTS()
    ismcts = ygogame.current_phase.run_simulation(ismcts)
    ismcts = ygogame.current_phase.run_simulation(ismcts) 
    assert len(ismcts.root.edges) == 2

    for i in range(20):
        ismcts = ygogame.current_phase.run_simulation(ismcts)
    assert len(ismcts.root.edges) == 2
    '''


if __name__ == '__main__':
    test_expand()


