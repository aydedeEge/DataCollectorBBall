from input.inputData import getSortedOrder, getDataPositionOrder, getSortedOrderForDay, getInputForDay
import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from neuralNet import NeuralNet
from keras import optimizers
import json
import keras
import time
import csv
from itertools import permutations
from keras.wrappers.scikit_learn import KerasRegressor

RANDOM_SEED = 588
TEST_SIZE_PERCENT = 0.3
EPOCH_COUNT = 10000
DEFAUL_HIDDEN_LAYERS = [32, 32]
DEFAUL_LEARNING_RATE = 0.01
DEFAULT_OPTIMIZER = lambda x: keras.optimizers.Adam(lr=x)
DEFAULT_BATCH_SIZE = 10000
DEFAULT_DROPOUT = 0
MIN_GAMES_PER_DAY = 8


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
        if (len(data) > 0):
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
    print("Training on :" + str(len(train_y_flat)) + "games")
    model = make_model(
        hidden_layer_sizes=DEFAUL_HIDDEN_LAYERS,
        learning_r=DEFAUL_LEARNING_RATE,
        batch_size_2=DEFAULT_BATCH_SIZE,
        dropout_rate=DEFAULT_DROPOUT)

    model.fit(train_x_flat, train_y_flat)

    # save the model
    model.save("trainedModels/nn_model_hn" + str(DEFAUL_HIDDEN_LAYERS[0]) +
               "_lr" + str(DEFAUL_LEARNING_RATE) + ".json")


def continue_training(train_X, train_y):
    pass


def test(train_X, test_X, train_y, test_y):
    model_loaded = NeuralNet.load("trainedModels/nn_model_hn" + str(
        DEFAUL_HIDDEN_LAYERS[0]) + "_lr" + str(DEFAUL_LEARNING_RATE) + ".json")
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


def make_model(hidden_layer_sizes, learning_r, batch_size_2, dropout_rate):
    input_size = 29
    output_size = 14
    optimizer = DEFAULT_OPTIMIZER(learning_r)
    loss = 'mean_squared_error'
    return NeuralNet(None, input_size, output_size, hidden_layer_sizes,
                     optimizer, loss, batch_size_2, dropout_rate)


def score_for_crossval(estimator, X, Y):
    score = []
    total_games = len(X)
    for i in range(total_games):
        start_day_i = i * MIN_GAMES_PER_DAY
        end_day_i = i * MIN_GAMES_PER_DAY + MIN_GAMES_PER_DAY
        if end_day_i > len(X):
            end_day_i = len(X)
            break
        artificial_day_X = X[start_day_i:end_day_i]
        artificial_day_Y = Y[start_day_i:end_day_i]
        day_score = estimator.model.scoreDay(artificial_day_X,
                                             artificial_day_Y)
        score.append(day_score)
    print(np.average(score))
    return np.average(score)


def combinations(n, list, combos=[]):
    # initialize combos during the first pass through
    if combos is None:
        combos = []

    if len(list) == n:
        # when list has been dwindeled down to size n
        # check to see if the combo has already been found
        # if not, add it to our list
        if combos.count(list) == 0:
            combos.append(list)
            combos.sort()
        return combos
    else:
        # for each item in our list, make a recursive
        # call to find all possible combos of it and
        # the remaining items
        for i in range(len(list)):
            refined_list = list[:i] + list[i + 1:]
            combos = combinations(n, refined_list, combos)
        return combos


def cross_val(train_X, train_y):
    train_x_flat = np.array([item for items in train_X for item in items])
    train_y_flat = np.array([item for items in train_y for item in items])
    print("Training on" + str(len(train_y_flat)))

    l_rs = [0.005,0.01,0.02,0.05,0.1,0.2]
    hidden_layer_sizes = [[64, 64], [32, 128], [32, 32, 32], [64, 64, 64],
                          [128, 64, 128]]
    batch_sizes = [10000,5000,250]
    dropout_rates = [0.25,0.5]
    params = {
        'hidden_layer_sizes': hidden_layer_sizes,
        'learning_r': l_rs,
        'batch_size_2': batch_sizes,
        'dropout_rate': dropout_rates
    }
    my_classifier = KerasRegressor(make_model)
    validator = GridSearchCV(
        estimator=my_classifier,
        param_grid=params,
        n_jobs=1,
        scoring=score_for_crossval)

    validator.fit(train_x_flat, train_y_flat,verbose=10)

    validator.cv_results_.pop('params', None)
    keys = validator.cv_results_.keys()
    #output resutl of gridsearch to file
    filename = "NN_result_trained_" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
    with open(filename, 'w') as outfile:
        csv_writer = csv.writer(
            outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(keys)
        for i in validator.cv_results_['rank_test_score']:
            row = []
            for k in keys:
                if k == 'param_hidden_layer_sizes':
                    a = '-'.join(
                        str(e) for e in validator.cv_results_[k][i - 1])
                    row = row + [a]
                else:
                    row = row + [str(validator.cv_results_[k][i - 1])]
            csv_writer.writerow(row)


def main():
    train_X, test_X, train_y, test_y = get_data()
    train(train_X, train_y)
    #test(train_X, test_X, train_y, test_y)
    predict('2018-03-28')


if __name__ == '__main__':
    main()
