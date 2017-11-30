
import tensorflow as tf
import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split

from input.inputData import getSortedOrder, getAverageAndDistribution, getDataPositionOrder

RANDOM_SEED = 527
tf.set_random_seed(RANDOM_SEED)
NUMBER_OF_HIDDEN_NODES = 128
LEARNING_RATE = 0.02
TEST_SIZE_PERCENT = 0.33
ACTIVATION_FUNCTION = tf.nn.sigmoid


def init_weights(shape):
    # randomo weight init
    weights = tf.random_normal(shape, stddev=0.1)
    return tf.Variable(weights)


def forwardprop(X, w_1, w_2):
    inputToFirstLayer = tf.matmul(X, w_1)
    outputFirstLayer = ACTIVATION_FUNCTION(inputToFirstLayer)
    yhat = tf.matmul(outputFirstLayer, w_2)  # The varphi function

    return yhat


def categorize(output):
    for y in output:
        if y[0] < 0:
            y[0] = -1
        elif y[0] > 0:
            y[0] = 1
    return output


def get_data():
    # choose which type of data to get
    data, target = getSortedOrder()
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
    return train_test_split(all_X, all_Y, test_size=TEST_SIZE_PERCENT, random_state=RANDOM_SEED)

def thresholdToTest(x,y):
    thresholdX = []
    thresholdY = []
    for i in range(len(y)):
        diff = y[i][0]-y[i][1]
        if diff< -0.5 or diff > 0.5:
            thresholdX.append(x[i])
            thresholdY.append(y[i])
    return thresholdX ,thresholdY 

def main():
    train_X, test_X, train_y, test_y = get_data()
    aboveTrain_X, aboveTrain_y = thresholdToTest(train_X, train_y)
    aboveTest_X, aboveTest_y = thresholdToTest(test_X, test_y)
    print(len(aboveTrain_X))
    print(len(aboveTest_X))
    # Layer's sizes
    x_size = train_X.shape[1]
    h_size = NUMBER_OF_HIDDEN_NODES
    y_size = train_y.shape[1]

    # thing that will be fed to the neural net
    X = tf.placeholder("float", shape=[None, x_size])
    y = tf.placeholder("float", shape=[None, y_size])

    # Weight initializations
    w_1 = init_weights((x_size, h_size))
    w_2 = init_weights((h_size, y_size))

    # Forward propagation
    yhat = forwardprop(X, w_1, w_2)
    predict = tf.argmax(yhat, axis=1)

    # ackward propagation
    # cost = tf.reduce_sum(tf.square(yhat - y)) / 4
    cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=yhat))
    updates = tf.train.GradientDescentOptimizer(LEARNING_RATE).minimize(cost)

    # Run SGD
    sess = tf.Session()
    init = tf.global_variables_initializer()
    sess.run(init)

    for epoch in range(500):

        for i in range(len(train_X)):
            # print(train_y[i: i + 1])
            sess.run(updates, feed_dict={X: train_X[i: i + 1], y: train_y[i: i + 1]})

        currentCost = sess.run(cost, feed_dict={X: train_X, y: train_y})
       
        train_accuracy = np.mean(np.argmax(aboveTrain_X, axis=1) ==  sess.run(predict, feed_dict={X: aboveTrain_X, y: aboveTrain_y}))
       
        test_accuracy = np.mean(np.argmax(aboveTest_X, axis=1) == sess.run(predict, feed_dict={X: aboveTest_X, y: aboveTest_y}))
        print("Epoch = %d, cost = %.5f train accuracy = %.2f%%, test accuracy = %.2f%%"
              % (epoch + 1, currentCost, 100. * train_accuracy, 100. * test_accuracy))

    sess.close()


if __name__ == '__main__':
    main()
