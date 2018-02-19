from input.inputData import getSortedOrder, getAverageAndDistribution, getDataPositionOrder
import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split
from neuralNet import NeuralNet
import json

RANDOM_SEED = 588
TEST_SIZE_PERCENT = 0.33
NUMBER_OF_HIDDEN_NODES = 128
LEARNING_RATE = 0.01


def get_data():
    # choose which type of data to get
    data, target = getDataPositionOrder()
    print("Data size : ", str(len(target)))
    print("Input form : ", data[0])
    print("Output form : ", target[0])

    N, M = data.shape
    # Add ones as x0 for bias = [1,score1,score2,....,scoren]
    all_X = np.ones((N, M + 1))
    all_X[:, 1:] = data
    # Only to get output labels, not use for analog
    # num_labels = len(np.unique(target.flatten()))
    # all_Y = np.eye(num_labels)[target.flatten()]
    all_Y = target
    return train_test_split(
        all_X, all_Y, test_size=TEST_SIZE_PERCENT, random_state=RANDOM_SEED)


def main():
    train_X, test_X, train_y, test_y = get_data()

    model = NeuralNet("trainedModels/tf.model.test_hn" +
                      str(NUMBER_OF_HIDDEN_NODES) + "_lr" + str(LEARNING_RATE))
    model.train_and_test(train_X, test_X, train_y, test_y,
                         NUMBER_OF_HIDDEN_NODES, LEARNING_RATE)

    print("final train accuracy:", model.score(train_X, train_y))
    print("final test accuracy:", model.score(test_X, test_y))

    # save the model
    model.save("trainedModels/nn_model_hn" + str(NUMBER_OF_HIDDEN_NODES) + "_lr" +
               str(LEARNING_RATE) + ".json")

    # load and score again
    model = NeuralNet.load("trainedModels/nn_model_hn" + str(NUMBER_OF_HIDDEN_NODES) +
                           "_lr" + str(LEARNING_RATE) + ".json")
    print("final train accuracy (after reload):", model.score(
        train_X, train_y))
    print("final test accuracy (after reload):", model.score(test_X, test_y))


if __name__ == '__main__':
    main()