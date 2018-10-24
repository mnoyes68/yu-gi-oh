import cards
import player
import game 
import random
import json
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import sgd

def initialize_network():
    # parameters
    epsilon = .1  # exploration
    num_actions = 3  # [move_left, stay, move_right]
    epoch = 1000
    max_memory = 500
    hidden_size = 40
    batch_size = 50

    model = Sequential()
    model.add(Dense(hidden_size, input_shape=(2, 20), activation='relu'))
    model.add(Dense(hidden_size, activation='relu'))
    model.add(Dense(num_actions))
    model.compile(sgd(lr=.2), "mse")

### Code to play the game

# Create Cards
def create_deck(json):
    deck_list = []
    for c in json:
        card = cards.MonsterCard(c.get('name'), c.get('id'), c.get('atk'), c.get('defn'), c.get('level'))
        deck_list.append(card)
    deck = cards.Deck(deck_list)
    return deck

### main
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





