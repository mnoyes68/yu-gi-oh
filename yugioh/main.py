import cards
import player
import game 
import json
import csv
import os
import logging

from keras.models import Sequential, load_model
from keras.layers.core import Dense
from keras.optimizers import sgd

def initialize_network():
    # parameters
    hidden_size = 40

    model = Sequential()
    # model.add(Dense(hidden_size, input_shape=(40,), activation='relu'))
    model.add(Dense(hidden_size, input_shape=(2, 20), activation='relu'))
    model.add(Dense(hidden_size, activation='sigmoid'))
    model.add(Dense(1))
    model.compile(sgd(lr=.2), "mse")

    return model

# Code to play the game

# Create Cards
def create_deck(json):
    deck_list = []
    for c in json:
        card = cards.MonsterCard(c.get('name'), c.get('id'), c.get('atk'), c.get('defn'), c.get('level'))
        deck_list.append(card)
    deck = cards.Deck(deck_list)
    return deck

def run_training_game(deck_json):
    yugi_deck = create_deck(deck_json)
    opp_deck = create_deck(deck_json)

    yugi = player.ComputerPlayer("Yugi", yugi_deck, None)
    opponent = player.ComputerPlayer("Opponent", opp_deck, None)

    ygogame = game.Game(yugi, opponent)
    ygogame.play_game()
    winner = ygogame.winner
    print "The winner is " + winner.name
    if winner == yugi:
        victory = True
    else:
        victory = False
    return yugi.memory, victory


# main
if __name__ == "__main__":
    #model = initialize_network()
    #model.load_weights("model.sameweights.h5")

    logging.basicConfig(filename='yugioh_game.log', level=logging.INFO, filemode='w')
    id_counter = 1

    with open("decks/yugi.json", "r") as deck:
        deck_json = json.loads(deck.read())

    with open('conv_training_data.json', 'w') as data_file, open('conv_training_results.csv', 'w') as result_file:
        fieldnames = ['ID', 'Result']
        writer = csv.writer(result_file, delimiter=',')
        writer.writerow(fieldnames)
        data_file.write('[')
        #while id_counter < 3250000:
        for i in range(0,1):
            memory, victory = run_training_game(deck_json)
            for state in memory:
                state['ID'] = id_counter
                if victory:
                    writer.writerow([id_counter, 1])
                else:
                    writer.writerow([id_counter, 0])
                json.dump(state, data_file, indent=4)
                data_file.write(',\n')
                id_counter += 1
        data_file.seek(-1, os.SEEK_END)
        data_file.truncate()
        data_file.seek(-1, os.SEEK_END)
        data_file.truncate()
        data_file.write(']')
        data_file.close()
        result_file.close()
    '''
    with open('small_test_data.json', 'w') as data_file, open('small_test_results.csv', 'w') as result_file:
        fieldnames = ['ID', 'Result']
        writer = csv.writer(result_file, delimiter=',')
        writer.writerow(fieldnames)
        data_file.write('[')
        for i in range(0,300):
        #while id_counter < 4000000:
            memory, victory = run_training_game(deck_json)
            for state in memory:
                state['ID'] = id_counter
                if victory:
                    writer.writerow([id_counter, 1])
                else:
                    writer.writerow([id_counter, 0])
                json.dump(state, data_file, indent=4)
                data_file.write(',\n')
                id_counter += 1
        data_file.seek(-1, os.SEEK_END)
        data_file.truncate()
        data_file.seek(-1, os.SEEK_END)
        data_file.truncate()
        data_file.write(']')
        data_file.close()
        result_file.close()
        '''






