import cards
import player
import game 
import random
import json
import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import sgd

def create_deck(json):
    deck_list = []
    for c in json:
        card = cards.MonsterCard(c.get('name'), c.get('id'), c.get('atk'), c.get('defn'), c.get('level'))
        deck_list.append(card)
    deck = cards.Deck(deck_list)
    return deck

def create_game():
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
    return ygogame

def draw_battle_state():

if __name__ == "__main__":
    # parameters
    epsilon = .1  # exploration
    num_actions = 3  # [move_left, stay, move_right]
    epoch = 1000
    max_memory = 500
    hidden_size = 40
    batch_size = 50
    grid_size = 10

    model = Sequential()
    model.add(Dense(hidden_size, input_shape=(2, 20), activation='relu'))
    model.add(Dense(hidden_size, activation='relu'))
    model.add(Dense(num_actions))
    model.compile(sgd(lr=.2), "mse")

    # If you want to continue training from a previous model, just uncomment the line bellow
    # model.load_weights("model.h5")

    # Define environment/game
    # env = Catch(grid_size)

    # Initialize experience replay object
    exp_replay = ExperienceReplay(max_memory=max_memory)

    # Train
    win_cnt = 0
    for e in range(epoch):
        loss = 0.
        env = create_game()
        env.play_game()
        game_over = False
        # get initial input, draws board and combines all rows into a single vector
        input_t = env.observe()

        while not game_over:
            input_tm1 = input_t
            # get next action, random 1 out of 10 times, otherwise predicts
            if np.random.rand() <= epsilon:
                action = np.random.randint(0, num_actions, size=1)
            else:
                q = model.predict(input_tm1)
                action = np.argmax(q[0])

            # apply action, get rewards and new state
            input_t, reward, game_over = env.act(action)
            if reward == 1:
                win_cnt += 1

            # store experience
            exp_replay.remember([input_tm1, action, reward, input_t], game_over)

            # adapt model
            inputs, targets = exp_replay.get_batch(model, batch_size=batch_size)

            #loss += model.train_on_batch(inputs, targets)[0]
            loss += model.train_on_batch(inputs, targets)
        print("Epoch {:03d}/999 | Loss {:.4f} | Win count {}".format(e, loss, win_cnt))

    # Save trained model weights and architecture, this will be used by the visualization code
    model.save_weights("model.h5", overwrite=True)
    with open("model.json", "w") as outfile:
        json.dump(model.to_json(), outfile)