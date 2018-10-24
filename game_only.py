import cards
import player
import game 
import random
import json

def create_deck(json):
    deck_list = []
    for c in json:
        card = cards.MonsterCard(c.get('name'), c.get('id'), c.get('atk'), c.get('defn'), c.get('level'))
        deck_list.append(card)
    deck = cards.Deck(deck_list)
    return deck

if __name__ == "__main__":
    with open("decks/yugi.json", "r") as deck:
        deck_json = json.loads(deck.read())
        yugi_deck = create_deck(deck_json)
        
    with open("decks/yugi.json", "r") as deck:
        deck_json = json.loads(deck.read())
        opp_deck = create_deck(deck_json)


    # Create Players
    yugi = player.ComputerPlayer("Yugi", yugi_deck)
    opponent = player.ComputerPlayer("Opponent", opp_deck)

    ygogame = game.Game(yugi, opponent)
    ygogame.play_game()

    print "The winner is " + ygogame.winner.name