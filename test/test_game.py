import sys
import os
import logging
import json
import pytest

sys.path.append(os.path.join(os.path.abspath("."), "yugioh"))

from ISMCTS import Node, ISMCTS
import cards
import player
import game


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


def run_training_game(deck_json):
    ygogame = create_training_game(deck_json)
    ygogame.play_game()


@pytest.mark.skip()
def test_iterate():
    logging.basicConfig(filename='ismcts.log', level=logging.INFO, filemode='w')

    with open("decks/yugi.json", "r") as deck:
        deck_json = json.loads(deck.read())
        ygogame = create_training_game(deck_json)

        ygogame.initialize_game()
        assert isinstance(ygogame.current_phase, game.DrawPhase)

        ygogame.play_phase()
        assert isinstance(ygogame.current_phase, game.MainPhase)

        ygogame.play_phase()
        assert isinstance(ygogame.current_phase, game.MainPhase2)

        ygogame.play_phase()
        assert isinstance(ygogame.current_phase, game.DrawPhase)

        ygogame.play_phase()
        assert isinstance(ygogame.current_phase, game.MainPhase)

        ygogame.play_phase()
        assert isinstance(ygogame.current_phase, game.BattlePhase)

        ygogame.play_phase()
        assert isinstance(ygogame.current_phase, game.MainPhase2)


@pytest.mark.skip()
def test_iterate_step():
    logging.basicConfig(filename='ismcts.log', level=logging.INFO, filemode='w')

    with open("decks/yugi.json", "r") as deck:
        deck_json = json.loads(deck.read())
        ygogame = create_training_game(deck_json)

        ygogame.initialize_game()
        assert isinstance(ygogame.current_phase, game.DrawPhase)

        ygogame.play_step()
        assert isinstance(ygogame.current_phase, game.MainPhase)

        ygogame.play_step()
        assert isinstance(ygogame.current_phase, game.MainPhase2)

        ygogame.play_step()
        assert isinstance(ygogame.current_phase, game.DrawPhase)

        ygogame.play_step()
        assert isinstance(ygogame.current_phase, game.MainPhase)

        ygogame.play_step()
        assert isinstance(ygogame.current_phase, game.BattlePhase)


if __name__ == '__main__':
    ### Test TBD game ends on draw phase
    test_iterate_battle_phase()


