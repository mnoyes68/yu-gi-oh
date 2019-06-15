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


def test_iterate_battle_phase():
    logging.basicConfig(filename='ismcts.log', level=logging.INFO, filemode='w')

    with open("decks/yugi.json", "r") as deck:
        deck_json = json.loads(deck.read())
        ygogame = create_training_game(deck_json)

        ygogame.initialize_game()
        is_battle_phase = False
        while not is_battle_phase:
            ygogame.play_step()
            is_battle_phase = isinstance(ygogame.current_phase, game.BattlePhase)

        assert len(ygogame.get_player().board.get_monsters()) == 1 and len(ygogame.get_opponent().board.get_monsters()) == 1
        m1 = ygogame.get_player().board.get_monsters()[0]
        m2 = ygogame.get_opponent().board.get_monsters()[0]
        atk1 = m1.atk 
        atk2 = m2.atk

        ygogame.play_step()

        if atk1 < atk2:
            assert len(ygogame.get_player().board.get_monsters()) == 0 and len(ygogame.get_opponent().board.get_monsters()) == 1
        elif atk1 > atk2:
            assert len(ygogame.get_opponent().board.get_monsters()) == 0 and len(ygogame.get_player().board.get_monsters()) == 1



if __name__ == '__main__':
    ### Test TBD game ends on draw phase
    test_iterate_battle_phase()


