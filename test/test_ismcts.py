import sys
import os
import logging
import json

sys.path.append(os.path.join(os.path.abspath("."), "yugioh"))

from ISMCTS import Node, ISMCTS
import cards
import player
import game


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


def test_game_ismcts():
    ygogame = create_and_launch_game()
    while not isinstance(ygogame.current_phase, game.BattlePhase):
        ygogame.play_phase()

    tree = ygogame.current_phase.buildISMCTS()
    assert tree.root.player.life_points == 4000


def test_custom_ismcts():
    ygogame = create_and_launch_game()
    yugi = ygogame.p1
    opponent = ygogame.p2

    node = Node(yugi, opponent, 1, True)
    tree = ISMCTS(node)

    node.player.life_points 
    assert tree.root.player.life_points == 4000
    assert opponent.life_points == 4000


if __name__ == '__main__':
    test_ismcts()


