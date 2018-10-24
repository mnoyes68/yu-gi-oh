import cards
import player
import game
import actions
import random
import json
import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import sgd
import pdb

def initialize_network():
    # parameters
    hidden_size = 40

    model = Sequential()
    model.add(Dense(hidden_size, input_shape=(40,), activation='relu'))
    model.add(Dense(hidden_size, activation='sigmoid'))
    model.add(Dense(1))
    model.compile(sgd(lr=.2), "mse")

    return model

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
    epoch = 50000
    memory = []
    results = []
    yugi_win_count = 0
    opp_win_count = 0
    yugi_model = initialize_network()
    opp_model = initialize_network()
    result_csv = open("training_results.csv","w") 

    for i in range(epoch):
        yugi_game_count = 0
        opp_game_count = 0
        #pdb.set_trace()
        if len(memory) > 0:
            mem_array = np.concatenate(memory)
            res_array = np.array(results)
            opp_model.fit(mem_array, res_array)
            del memory[:]
            del results[:]
        while yugi_game_count < 4 and opp_game_count < 4:
            with open("decks/yugi.json", "r") as deck:
                deck_json = json.loads(deck.read())
                yugi_deck = create_deck(deck_json)
                
            with open("decks/yugi.json", "r") as deck:
                deck_json = json.loads(deck.read())
                opp_deck = create_deck(deck_json)

            # Create Players
            yugi = player.ComputerPlayer("Yugi", yugi_deck, yugi_model)
            opponent = player.ComputerPlayer("Opponent", opp_deck, opp_model)

            ygogame = game.Game(yugi, opponent)
            ygogame.play_game()

            winner = ygogame.winner
            print "The winner is " + winner.name
            if winner == yugi:
                yugi_game_count += 1
                win_mem = yugi.memory
                loss_mem = opponent.memory
                for i in win_mem:
                    memory.append(i)
                    results.append(1)
                for j in loss_mem:
                    memory.append(j)
                    results.append(0)
            elif winner == opponent:
                opp_game_count += 1
                win_mem = opponent.memory
                loss_mem = yugi.memory
                for i in win_mem:
                    memory.append(i)
                    results.append(1)
                for j in loss_mem:
                    memory.append(j)
                    results.append(0)
            else:
                print "ERROR: No winner found"
                break
            #pdb.set_trace()

            print "Series Score, Yugi: {0} | Opponent {1}".format(yugi_game_count, opp_game_count)
            print "Match Score, Yugi: {0} | Opponent {1}".format(yugi_win_count, opp_win_count)
        if yugi_game_count >= 4:
            yugi_win_count += 1
            print "Yugi wins match"
        elif opp_game_count >= 4:
            opp_win_count += 1
            yugi_model.set_weights(opp_model.get_weights())
            print "Opponent wins match"
        result_csv.write("{0},{1}\n".format(yugi_win_count, opp_win_count))
        #pdb.set_trace()
    print "Final Match Score, Yugi: {0} | Opponent {1}".format(yugi_win_count, opp_win_count)
    result_csv.close()
    yugi_model.save_weights("model.h5", overwrite=True)




