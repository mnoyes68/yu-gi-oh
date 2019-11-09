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
import copy

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

    p1 = copy.deepcopy(yugi)
    p2 = copy.deepcopy(opponent)

    ygogame = game.Game(yugi, opponent)
    return ygogame


def test_deepcopy():
    ygogame = create_and_launch_game()
    ygogame.play_game()
    i = 0
    '''
    while not ygogame.game_is_over:
    	print i
    	print ygogame.current_phase.__class__.__name__
    	ygogame.play_phase()
    '''


if __name__ == '__main__':
    test_deepcopy()