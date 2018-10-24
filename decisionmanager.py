import random
import operator
import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import sgd

class DecisionManager():
    def __init__(self, model):
        self.epsilon = .1  # exploration
        self.epoch = 1000
        self.max_memory = 500
        self.hidden_size = 40
        self.batch_size = 50
        self.grid_size = 10

        self.model = model
        '''
        self.model = Sequential()
        self.model.add(Dense(self.hidden_size, input_shape=(40,), activation='relu'))
        self.model.add(Dense(self.hidden_size, activation='relu'))
        self.model.add(Dense(1))
        self.model.compile(sgd(lr=.2), "mse")
        '''

    def make_decision(self, move_list):
        return random.choice(move_list)

    def make_decision_while_drawing(self, move_list):
        for move in move_list:
            move.draw_state()
        return random.choice(move_list)

    def make_network_decision(self, move_list):
        move_scores = {}
        for move in move_list:
            input_map = move.draw_state().reshape((1, -1))
            q = self.model.predict(input_map)
            print move.get_name() + ": " + str(q[0][0])
            move_scores[move] = q[0][0]
        top_move = max(move_scores.iteritems(), key=operator.itemgetter(1))[0]
        return top_move


