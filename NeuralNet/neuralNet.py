#used for saving stuff https://github.com/lazyprogrammer/machine_learning_examples/blob/master/ann_class2/tf_with_save.py
import tensorflow as tf
import numpy as np
import json
import keras
from accuracy import compute_accuracy, predict_lineup, get_lineups
from sklearn import datasets
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.models import model_from_json
from keras import backend as K

EPOCH_COUNT = 5000
VERBOSE = 1  # set it to 1 to see output, 0 to not see it


class NeuralNet:
    def __init__(self,
                 model=None,
                 input_size=None,
                 output_size=None,
                 hidden_layer_sizes=None,
                 optimizer=None,
                 loss=None,
                 batch_size=None,
                 dropout_rate=None,
                 epoch=EPOCH_COUNT):
        if model is None:
            self.model = Sequential()
            self.input_size = input_size
            self.output_size = output_size
            self.hidden_layer_sizes = hidden_layer_sizes
            self.optimizer = optimizer
            self.loss = loss
            self.batch_size = batch_size
            self.dropout_rate = dropout_rate
            self.epoch = epoch
            self.build()
        elif optimizer is not None:
            print("use previous weights")
            self.model = model
            self.optimizer = optimizer
            self.loss = loss
            self.batch_size = batch_size
            self.epoch = epoch
            self.model.compile(
                loss=self.loss, optimizer=self.optimizer, metrics=['mae'])
        else:
            print("use previous weights")
            self.model = model

    def predict(self, X):
        return self.model.predict(X)

    def build(self):
        first_layer_size = self.hidden_layer_sizes[0]
        self.model.add(
            Dense(
                units=first_layer_size,
                activation='sigmoid',
                input_dim=self.input_size))
        self.model.add(Dropout(self.dropout_rate))
        for layer_size in self.hidden_layer_sizes[1:]:
            self.model.add(Dense(units=layer_size, activation='sigmoid'))
            self.model.add(Dropout(self.dropout_rate))

        self.model.add(Dense(units=self.output_size))
        self.model.compile(
            loss=self.loss, optimizer=self.optimizer, metrics=['mae'])
        if VERBOSE == 1:
            self.model.summary()

    def score(self, X, Y):
        score = []
        for i in range(len(X)):
            score.append(self.scoreDay(X[i], Y[i]))
        return np.average(score)

    def scoreDay(self, X_day, Y_day, returnLineup=False):
        y_predicted = self.predict(X_day)
        return compute_accuracy(y_predicted, Y_day, returnLineup)

    def getPrediction(self, X_day, players, num_lineups):
        y_predicted = self.predict(X_day)
        player_expectedScore = [
            item for items in y_predicted for item in items
        ]
        for i in range(len(players)):
            players[i].expectedScore = player_expectedScore[i]
        expected_score, selected_lineup = predict_lineup(players)
        if (num_lineups > 0):
            expected_scores_noisy, selected_lineups_noisy = get_lineups(
                players, num_lineups + 1)
            expected_score = expected_score + expected_scores_noisy
            selected_lineup = selected_lineup + selected_lineups_noisy
        return expected_score, selected_lineup

    def save(self, filename):
        model_json = self.model.to_json()
        with open(filename, "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.model.save_weights(filename + "model.h5")

    @staticmethod
    def load(filename):
        json_file = open(filename, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights(filename + "model.h5")
        return loaded_model

    def fit(self, train_X, train_y):
        self.model.fit(
            train_X,
            train_y,
            epochs=self.epoch,
            batch_size=self.batch_size,
            verbose=VERBOSE)
