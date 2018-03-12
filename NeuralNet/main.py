from input.inputData import getSortedOrder, getDataPositionOrder, getSortedOrderForDay, getInputForDay
import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split
from neuralNet import NeuralNet
import json

RANDOM_SEED = 588
TEST_SIZE_PERCENT = 0.3
NUMBER_OF_HIDDEN_NODES = 64
LEARNING_RATE = 0.01
MIN_GAMES_PER_DAY = 7
EPOCH_COUNT = 500


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
            print("Data size : ", str(len(target)))
            print("Input form : ", data[0])
            print("Output form : ", target[0])


            N, M = data.shape
            # Add ones as x0 for bias = [1,score1,score2,....,scoren]
            day_X = np.ones((N, M + 1))
            day_X[:, 1:] = data
            day_Y = target

            grouped_X.append(day_X)
            grouped_y.append(day_Y)
        elif (len(data) == 0):
            print("Not data on this day " + str(i))
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
    model = NeuralNet("trainedModels/tf.model.test_hn" +
                      str(NUMBER_OF_HIDDEN_NODES) + "_lr" + str(LEARNING_RATE))
    model.train_and_test(train_x_flat, train_y_flat, NUMBER_OF_HIDDEN_NODES,
                         LEARNING_RATE, EPOCH_COUNT)

    # save the model
    model.save("trainedModels/nn_model_hn" + str(NUMBER_OF_HIDDEN_NODES) +
               "_lr" + str(LEARNING_RATE) + ".json")


def continue_training(train_X, train_y):
    pass


def test(train_X, test_X, train_y, test_y):
    model = NeuralNet.load("trainedModels/nn_model_hn" + str(
        NUMBER_OF_HIDDEN_NODES) + "_lr" + str(LEARNING_RATE) + ".json")
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

    N, M = day_x.shape
    day_X = np.ones((N, M + 1))
    day_X[:, 1:] = day_x
    model = NeuralNet.load("trainedModels/nn_model_hn" + str(
        NUMBER_OF_HIDDEN_NODES) + "_lr" + str(LEARNING_RATE) + ".json")

    score, predictedLineup = model.getPrediction(day_X, playerList)

    print("player selected:")
    for player in predictedLineup:
        print(player.toString())


def main():
    train_X, test_X, train_y, test_y = get_data()
    #train(train_X, train_y)
    test(train_X, test_X, train_y, test_y)

    predict('2017-03-25')

if __name__ == '__main__':
    main()
