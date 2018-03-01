from input.inputData import getSortedOrder, getDataPositionOrder, getSortedOrderForDay
import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split
from neuralNet import NeuralNet
import json

RANDOM_SEED = 588
TEST_SIZE_PERCENT = 0.33
NUMBER_OF_HIDDEN_NODES = 128
LEARNING_RATE = 0.01
EPOCH_COUNT = 10


def get_data():
    # choose which type of data to get
    all_data, all_targets = getDataPositionOrder()
    grouped_X = []
    grouped_y = []
    day_count = len(all_data)
    for i in range(0, day_count):
        data = np.array(all_data[i])
        target = np.array(all_targets[i])

        if (len(data) != 0):
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
        else:
            print("No data on this day " + str(i))

    return train_test_split(
        np.array(grouped_X),
        np.array(grouped_y),
        test_size=TEST_SIZE_PERCENT,
        random_state=RANDOM_SEED)


def train(train_X, train_y):
    train_x_flat = np.array([item for items in train_X for item in items])
    train_y_flat = np.array([item for items in train_y for item in items])

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
    day_x, day_y = getSortedOrderForDay(day)
    N, M = day_x.shape
    day_X = np.ones((N, M + 1))
    day_X[:, 1:] = day_x
    model = NeuralNet.load("trainedModels/nn_model_hn" + str(
        NUMBER_OF_HIDDEN_NODES) + "_lr" + str(LEARNING_RATE) + ".json")
    score, realLineup, predictedLineup = model.scoreDay(day_X, day_y, True)
    print("test accuracy for day:", score)
    print("good players:", realLineup)
    print("player selected:", predictedLineup)
    #Todo return names of player


def main():
    train_X, test_X, train_y, test_y = get_data()
    test(train_X, test_X, train_y, test_y)

    #run('2017-03-20')


if __name__ == '__main__':
    main()
