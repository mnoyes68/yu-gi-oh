import cards
import player
import game

import logging
import json
import csv
import os


# Create Cards
def create_deck(json):
    deck_list = []
    for c in json:
        card = cards.MonsterCard(c.get('name'), c.get('id'), c.get('atk'), c.get('defn'), c.get('level'))
        deck_list.append(card)
    deck = cards.Deck(deck_list)
    return deck

def run_game(deck_json):
    yugi_deck = create_deck(deck_json)
    opp_deck = create_deck(deck_json)

    yugi = player.ComputerPlayer("Yugi", yugi_deck, None)
    opponent = player.ComputerPlayer("Opponent", opp_deck, None)

    ygogame = game.Game(yugi, opponent)
    ygogame.play_game()
    winner = ygogame.winner
    print "The winner is " + winner.name


# main
if __name__ == "__main__":
    logging.basicConfig(filename='buildmcts.log', level=logging.INFO)
    with open("decks/yugi.json", "r") as deck:
        deck_json = json.loads(deck.read())
    run_game(deck_json)









