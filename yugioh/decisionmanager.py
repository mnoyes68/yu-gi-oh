import random
import operator
import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import sgd

class DecisionManager():
    def __init__(self):
        pass

    def make_decision(self, move_list):
        return random.choice(move_list)


class NetworkDecisionManager(DecisionManager):
    def __init__(self, model):
        DecisionManager.__init__(self)
        self.model = model

    def make_decision(self, move_list):
        move_scores = {}
        for move in move_list:
            input_map = move.draw_state().reshape((1, -1))
            q = self.model.predict(input_map)
            print move.get_name() + ": " + str(q[0][0])
            move_scores[move] = q[0][0]
        top_move = max(move_scores.iteritems(), key=operator.itemgetter(1))[0]
        return top_move


