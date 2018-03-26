#used for saving stuff https://github.com/lazyprogrammer/machine_learning_examples/blob/master/ann_class2/tf_with_save.py
import tensorflow as tf
import numpy as np
import json
import keras
from accuracy import compute_accuracy, predict_lineup
from sklearn import datasets
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json


class NeuralNet:
    def __init__(self, model=None):
        if model is None:
            self.model = Sequential()
            self.build(29, 14)
        else:
            self.model = model

    def predict(self, X):
        return self.model.predict(X)

    def build(self, x_size, y_size):
        self.model.add(Dense(units=64, activation='relu', input_dim=29))
        self.model.add(Dense(units=14, activation='softmax'))
        self.model.compile(
            loss='mean_squared_error',
            optimizer=keras.optimizers.SGD(lr=0.01, momentum=0.9),
            metrics=['accuracy'])

    def score(self, X, Y):
        score = []
        for i in range(len(X)):
            score.append(self.scoreDay(X[i], Y[i]))
        return np.average(score)

    def scoreDay(self, X_day, Y_day, returnLineup=False):
        y_predicted = self.predict(X_day)
        return compute_accuracy(y_predicted, Y_day, returnLineup)

    def getPrediction(self, X_day, players):
        y_predicted = self.predict(X_day)
        player_expectedScore = [
            item for items in y_predicted for item in items
        ]
        for i in range(len(players)):
            players[i].expectedScore = player_expectedScore[i]
        return predict_lineup(players)

    def save(self, filename):
        model_json = self.model.to_json()
        with open(filename, "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.model.save_weights("model.h5")

    @staticmethod
    def load(filename):
        json_file = open(filename, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights("model.h5")
        return loaded_model

    def train_and_test(self, train_X, train_y, hidden_nodes, learning_rate,
                       epoch):
        self.model.fit(train_X, train_y, epochs=5, batch_size=32)
