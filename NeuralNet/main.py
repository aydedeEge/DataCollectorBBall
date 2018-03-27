from input.inputData import getSortedOrder, getDataPositionOrder, getSortedOrderForDay, getInputForDay
import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.grid_search import GridSearchCV
from neuralNet import NeuralNet

import json
import keras
from keras.wrappers.scikit_learn import KerasRegressor

RANDOM_SEED = 588
TEST_SIZE_PERCENT = 0.3
NUMBER_OF_HIDDEN_NODES = 128
LEARNING_RATE = 0.0045
MIN_GAMES_PER_DAY = 0
EPOCH_COUNT = 2


def get_data():
    # choose which type of data to get
    all_data, all_targets = getDataPositionOrder()
    grouped_X = []
    grouped_y = []
    day_count = len(all_data)
    smaller_day_X = []
    smaller_day_y = []
    days = 0
    for i in range(0, day_count):
        data = np.array(all_data[i])
        target = np.array(all_targets[i])
        if (len(data) > MIN_GAMES_PER_DAY):
            days += 1
            # print("Data size : ", str(len(target)))
            # print("Input form : ", data[0])
            # print("Output form : ", target[0])

            N, M = data.shape
            # Add ones as x0 for bias = [1,score1,score2,....,scoren]
            day_X = np.ones((N, M + 1))
            day_X[:, 1:] = data
            day_Y = target

            grouped_X.append(day_X)
            grouped_y.append(day_Y)
    # elif (len(data) == 0):
    # print("Not data on this day " + str(i))
    print("Test on " + str(days) + " days over " + str(day_count))
    return train_test_split(
        np.array(grouped_X),
        np.array(grouped_y),
        test_size=TEST_SIZE_PERCENT,
        random_state=RANDOM_SEED)


def train(train_X, train_y):
    train_x_flat = np.array([item for items in train_X for item in items])
    train_y_flat = np.array([item for items in train_y for item in items])
    print(len(train_y_flat))
    # model = NeuralNet("trainedModels/tf.model.test_hn" +
    #                   str(NUMBER_OF_HIDDEN_NODES) + "_lr" + str(LEARNING_RATE))
    input_size = 29
    output_size = 14
    hidden_layer_sizes = [128, 128]
    optimizer = keras.optimizers.SGD(lr=LEARNING_RATE, momentum=0.9)
    loss = 'mean_squared_error'
    batch_size = 32
    dropout_rate = 0.5
    model = NeuralNet(None, input_size, output_size, hidden_layer_sizes,
                      optimizer, loss, batch_size, dropout_rate)
    #
    model.train_and_test(train_x_flat, train_y_flat, EPOCH_COUNT)

    # save the model
    # model.save("trainedModels/nn_model_hn" + str(NUMBER_OF_HIDDEN_NODES) +
    #            "_lr" + str(LEARNING_RATE) + ".json")


def continue_training(train_X, train_y):
    pass


def test(train_X, test_X, train_y, test_y):
    model_loaded = NeuralNet.load("trainedModels/nn_model_hn" + str(
        NUMBER_OF_HIDDEN_NODES) + "_lr" + str(LEARNING_RATE) + ".json")
    model = NeuralNet(model_loaded)
    print("final train accuracy:", model.score(train_X, train_y))
    print("final test accuracy:", model.score(test_X, test_y))


#format of day should be YYYY-MM-DD
def run(day):
    day_x, day_y, Gamesplayers = getSortedOrderForDay(day)
    playersList = [item.playerID for items in Gamesplayers for item in items]

    N, M = day_x.shape
    day_X = np.ones((N, M + 1))
    day_X[:, 1:] = day_x
    model = NeuralNet.load("trainedModels/nn_model_hn" + str(
        NUMBER_OF_HIDDEN_NODES) + "_lr" + str(LEARNING_RATE) + ".json")
    score, realLineupIndex, predictedLineupIndex = model.scoreDay(
        day_X, day_y, True)
    realLineup = [playersList[i] for i in realLineupIndex]
    predictedLineup = [playersList[i] for i in predictedLineupIndex]
    print("test accuracy for day:", score)
    print("good players ids:", realLineup)
    print("players selected ids :", predictedLineup)


def predict(day):
    day_x, playerList = getInputForDay(day)
    print(day_x.shape)
    print(len(playerList))
    N, M = day_x.shape
    day_X = np.ones((N, M + 1))
    day_X[:, 1:] = day_x
    model = NeuralNet.load("trainedModels/nn_model_hn" + str(
        NUMBER_OF_HIDDEN_NODES) + "_lr" + str(LEARNING_RATE) + ".json")

    score, predictedLineup = model.getPrediction(day_X, playerList)

    print("player selected:")
    for player in predictedLineup:
        print(player.toString())
    print("Score:" + str(score))


def make_model(model=None,
               input_size=None,
               output_size=None,
               hidden_layer_sizes=None,
               optimizer=None,
               loss=None,
               batch_size=None,
               dropout_rate=None):
    input_size = 29
    output_size = 14
    optimizer = keras.optimizers.SGD(lr=LEARNING_RATE, momentum=0.9)
    loss = 'mean_squared_error'
    batch_size = 32
    dropout_rate = 0.5
    return NeuralNet(model, input_size, output_size, hidden_layer_sizes,
                     optimizer, loss, batch_size, dropout_rate)


def score(estim, X, Y):
    score = []
    for i in range(len(X)):
        if i * 8 + 8 <= len(X):
            groupX = X[i * 8:i * 8 + 8]
            groupY = Y[i * 8:i * 8 + 8]
        else:
            groupX = X[i * 8:len(X)]
            groupY = Y[i * 8:len(X)]
            break
        sc = estim.model.scoreDay(groupX, groupY)
        score.append(sc)
    print(np.average(score))
    return np.average(score)


def cross_val(train_X, train_y):
    train_x_flat = np.array([item for items in train_X for item in items])
    train_y_flat = np.array([item for items in train_y for item in items])
    print("Training on" + str(len(train_y_flat)))
    params = {'hidden_layer_sizes': [[32,32], [32]]}

    my_classifier = KerasRegressor(make_model)
    validator = GridSearchCV(
        estimator=my_classifier, param_grid=params, n_jobs=1, scoring=score)

    validator.fit(train_x_flat, train_y_flat)


def main():
    train_X, test_X, train_y, test_y = get_data()
    cross_val(train_X, train_y)
    #test(train_X, test_X, train_y, test_y)
    #predict('2018-03-17')


if __name__ == '__main__':
    main()
