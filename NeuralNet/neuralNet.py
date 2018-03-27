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
from keras import backend as K


class NeuralNet:
    def __init__(self,
                 model=None,
                 input_size=None,
                 output_size=None,
                 hidden_layer_sizes=None,
                 optimizer=None,
                 loss=None):
        print(K.tensorflow_backend._get_available_gpus())
        if model is None:
            self.model = Sequential()
            self.input_size = input_size
            self.output_size = output_size
            self.hidden_layer_sizes = hidden_layer_sizes
            self.optimizer = optimizer
            self.loss = loss
            self.build()
        else:
            self.model = model

    def predict(self, X):
        return self.model.predict(X)

    def build(self):
        first_layer_size = self.hidden_layer_sizes.pop(0)
        self.model.add(
            Dense(
                units=first_layer_size,
                activation='sigmoid',
                input_dim=self.input_size))

        for layer_size in self.hidden_layer_sizes:
            self.model.add(Dense(units=layer_size, activation='sigmoid'))

        self.model.add(Dense(units=self.output_size))
        self.model.compile(
            loss=self.loss, optimizer=self.optimizer, metrics=['accuracy'])

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

    def train_and_test(self, train_X, train_y, epoch):
        self.model.fit(train_X, train_y, epochs=epoch, batch_size=10000)
