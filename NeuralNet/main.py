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
import sys
from itertools import permutations
from keras.wrappers.scikit_learn import KerasRegressor

RANDOM_SEED = 588
TEST_SIZE_PERCENT = 0.3
DEFAUL_HIDDEN_LAYERS = [64, 128]
DEFAULT_LEARNING_RATE = 0.001
DEFAULT_OPTIMIZER = lambda x: keras.optimizers.Adam(lr=x)
DEFAULT_BATCH_SIZE = 1000
DEFAULT_DROPOUT = 0.4
MIN_GAMES_PER_DAY = 8
FILENAME_USED_NN = "trainedModels/nn_model_hn" + str(
    DEFAUL_HIDDEN_LAYERS[0]) + "_lr" + str(DEFAULT_LEARNING_RATE) + ".json"

INPUT_SIZE = 43
OUTPUT_SIZE  = 14

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


def train(train_X, train_y, args):
    epoch = int(args[2])
    filename = FILENAME_USED_NN
    if len(args) == 4:
        filename = "trainedModels/" + args[3]
    train_x_flat = np.array([item for items in train_X for item in items])
    train_y_flat = np.array([item for items in train_y for item in items])
    print("Training on :" + str(len(train_y_flat)) + "games")
    model = make_model(
        hidden_layer_sizes=DEFAUL_HIDDEN_LAYERS,
        learning_r=DEFAULT_LEARNING_RATE,
        batch_size_2=DEFAULT_BATCH_SIZE,
        dropout_rate=DEFAULT_DROPOUT,
        epoch=epoch)

    model.fit(train_x_flat, train_y_flat)
    # save the model
    model.save(filename)


def continue_training(train_X, train_y, args):
    print("NOT SURE THIS IS WORKING")
    epoch = int(args[2])
    filename = FILENAME_USED_NN
    if len(args) == 4:
        filename = "trainedModels/" + args[3]
    train_x_flat = np.array([item for items in train_X for item in items])
    train_y_flat = np.array([item for items in train_y for item in items])
    model_loaded = NeuralNet.load(filename)
    
    model = make_model(
        model=model_loaded,
        learning_r=DEFAULT_LEARNING_RATE,
        batch_size_2=DEFAULT_BATCH_SIZE,
        epoch=epoch)
    print("Continue training on :" + str(len(train_y_flat)) + "games")
    model.fit(train_x_flat, train_y_flat)


def test(train_X, test_X, train_y, test_y, args):
    filename = FILENAME_USED_NN
    if len(args) == 3:
        filename = "trainedModels/" + args[2]
    model_loaded = NeuralNet.load(filename)
    model = NeuralNet(model_loaded)
    print("final train accuracy:", model.score(train_X, train_y))
    print("final test accuracy:", model.score(test_X, test_y))


#format of day should be YYYY-MM-DD
# UNUSED
def run(day):
    print("This mETHOD should not be being calleD!")
    day_x, day_y, Gamesplayers = getSortedOrderForDay(day)
    playersList = [item.playerID for items in Gamesplayers for item in items]

    N, M = day_x.shape
    day_X = np.ones((N, M + 1))
    day_X[:, 1:] = day_x
    model = NeuralNet.load(FILENAME_USED_NN)
    score, realLineupIndex, predictedLineupIndex = model.scoreDay(
        day_X, day_y, True)
    realLineup = [playersList[i] for i in realLineupIndex]
    predictedLineup = [playersList[i] for i in predictedLineupIndex]
    print("test accuracy for day:", score)
    print("good players ids:", realLineup)
    print("players selected ids :", predictedLineup)


def predict(args):
    day = args[2]
    num_lineups = int(args[3])
    filename = FILENAME_USED_NN
    if len(args) == 5:
        filename = "trainedModels/" + args[4]
    day_x, playerList = getInputForDay(day)
    print(day_x.shape)
    print(len(playerList))
    N, M = day_x.shape
    day_X = np.ones((N, M + 1))
    day_X[:, 1:] = day_x
    model = NeuralNet(NeuralNet.load(filename))

    scores, predictedLineups = model.getPrediction(day_X, playerList,
                                                   num_lineups)
    print()
    print("No noise lineup : ")
    for i in range(len(scores)):
        predictedLineup = predictedLineups[i]

        print("player selected:")
        for player in predictedLineup:
            print(player.toString())
        print()
        print("Expected total score :" + str(scores[i]))
        print("---------------")


def make_model(model=None,
               hidden_layer_sizes=None,
               learning_r=None,
               batch_size_2=None,
               dropout_rate=None,
               epoch=None):
    optimizer = DEFAULT_OPTIMIZER(learning_r)
    loss = 'mean_squared_error'
    return NeuralNet(model, INPUT_SIZE, OUTPUT_SIZE, hidden_layer_sizes,
                     optimizer, loss, batch_size_2, dropout_rate, epoch)


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


def cross_val(train_X, train_y, args):
    epoch = None
    filename = "NN_result_trained_" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
    if len(args) == 4:
        epoch = args[2]
        filename = args[3]
    train_x_flat = np.array([item for items in train_X for item in items])
    train_y_flat = np.array([item for items in train_y for item in items])
    print("Training on" + str(len(train_y_flat)))

    l_rs = [0.001, 0.01, 0.1]
    hidden_layer_sizes = [[64, 64], [32, 32, 32], [64, 64, 64], [128, 64, 128]]
    batch_sizes = [10000, 5000, 250]
    dropout_rates = [0.1, 0.25, 0.5]
    params = {
        'hidden_layer_sizes': hidden_layer_sizes,
        'learning_r': l_rs,
        'batch_size_2': batch_sizes,
        'dropout_rate': dropout_rates,
        'epoch': epoch
    }
    my_classifier = KerasRegressor(make_model)
    validator = GridSearchCV(
        estimator=my_classifier,
        param_grid=params,
        n_jobs=1,
        scoring=score_for_crossval,
        verbose=100)

    validator.fit(train_x_flat, train_y_flat)

    validator.cv_results_.pop('params', None)
    keys = validator.cv_results_.keys()
    #output resutl of gridsearch to file

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
    INPUT_SIZE = train_X[0][1] #not working?
    OUTPUT_SIZE = train_y[0][1]
    accepted_args = {
        "train":
        lambda args: train(train_X, train_y, args),
        "continue_training":
        lambda args: continue_training(train_X, train_y, args),
        "cross_val":
        lambda args: cross_val(train_X, train_y, args),
        "test":
        lambda args: test(train_X, test_X, train_y, test_y, args),
        "predict":
        predict,
    }
    try:
        accepted_args[sys.argv[1]](sys.argv)
    except Exception as e:
        print(e)
        print()
        print("Choose one of the options. filename.json is optional: ")
        print("train <#epoch> <filename.json>")
        print("continue_training <#epoch> <filename.jsonf>")
        print("cross_val <#epoch> <filename_result>")
        print("test <filename.json>")
        print("predict <date> <#of_noisy_result> <filename.json>")
        return


if __name__ == '__main__':
    main()
