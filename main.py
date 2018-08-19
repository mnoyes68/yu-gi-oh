import cards
import player
import game 
import random
import json

# Create Cards
def create_deck(json):
    deck_list = []
    for c in json:
        print c
        print c.get('name')
        card = cards.MonsterCard(c.get('name'), c.get('id'), c.get('atk'), c.get('defn'), c.get('level'))
        deck_list.append(card)
    deck = cards.Deck(deck_list)
    return deck


with open("decks/yugi.json", "r") as deck:
    deck_json = json.loads(deck.read())
    print deck_json
    yugi_deck = create_deck(deck_json)
    
with open("decks/yugi.json", "r") as deck:
    deck_json = json.loads(deck.read())
    opp_deck = create_deck(deck_json)


# Create Players
yugi = player.ComputerPlayer("Yugi", yugi_deck)
opponent = player.ComputerPlayer("Opponent", opp_deck)

ygogame = game.Game(yugi, opponent)
ygogame.play_game()





