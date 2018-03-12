#used for saving stuff https://github.com/lazyprogrammer/machine_learning_examples/blob/master/ann_class2/tf_with_save.py
import tensorflow as tf
import numpy as np
import json
from accuracy import compute_accuracy
from sklearn import datasets
from sklearn.model_selection import train_test_split

RANDOM_SEED = 588


class NeuralNet:
    def __init__(self,
                 savefile,
                 hidden_nodes=None,
                 learning_rate=None,
                 x_size=None,
                 y_size=None):
        self.savefile = savefile
        tf.set_random_seed(RANDOM_SEED)
        if hidden_nodes and learning_rate and x_size and y_size:
            self.hidden_nodes = hidden_nodes
            self.learning_rate = learning_rate
            self.build(x_size, y_size)

    def forwardprop(self):
        inputToFirstLayer = tf.matmul(self.X, self.W1)
        outputFirstLayer = tf.nn.sigmoid(inputToFirstLayer)
        yhat = tf.matmul(outputFirstLayer, self.W2)  # The varphi function
        return yhat

    def predict(self, X):
        with tf.Session() as session:
            # restore the model
            self.saver.restore(session, self.savefile)
            P = session.run(self.predict_op, feed_dict={self.X: X})
        return P

    def build(self, x_size, y_size):
        self.x_size = x_size
        self.y_size = y_size
        # define variables and expressions
        self.X = tf.placeholder(tf.float32, shape=(None, x_size), name='X')
        self.y = tf.placeholder(tf.float32, shape=(None, y_size), name='y')

        self.W1 = tf.Variable(
            tf.random_normal((x_size, self.hidden_nodes), stddev=0.1),
            name='W1')
        self.W2 = tf.Variable(
            tf.random_normal((self.hidden_nodes, y_size), stddev=0.1),
            name='W2')

        self.saver = tf.train.Saver({'W1': self.W1, 'W2': self.W2})

        # Forward propagation
        yhat = self.forwardprop()
        self.predict_op = yhat

        # ackward propagation
        cost = tf.reduce_sum(tf.square(yhat - self.y)) / 4
        return cost

    def score(self, X, Y):
        score = []
        for i in range(len(X)):
            score.append(self.scoreDay(X[i], Y[i]))
        return np.average(score)

    def scoreDay(self, X_day, Y_day, returnLineup=False):
        y_predicted = self.predict(X_day)
        return compute_accuracy(y_predicted, Y_day, returnLineup)

    def save(self, filename):
        j = {
            'HD': self.hidden_nodes,
            'LR': self.learning_rate,
            'X_M': self.x_size,
            'Y_M': self.y_size,
            'model': self.savefile
        }
        with open(filename, 'w') as f:
            json.dump(j, f)

    @staticmethod
    def load(filename):
        with open(filename) as f:
            j = json.load(f)
            return NeuralNet(j['model'], j['HD'], j['LR'], j['X_M'], j['Y_M'])

    def train_and_test(self, train_X, train_y, hidden_nodes, learning_rate,
                       epoch):

        self.hidden_nodes = hidden_nodes
        self.learning_rate = learning_rate
        cost = self.build(train_X.shape[1], train_y.shape[1])
        updates = tf.train.GradientDescentOptimizer(
            self.learning_rate).minimize(cost)

        init = tf.global_variables_initializer()

        with tf.Session() as sess:
            sess.run(init)
            for epoch in range(epoch):

                for i in range(len(train_X)):
                    # print(train_y[i: i + 1])
                    sess.run(
                        updates,
                        feed_dict={
                            self.X: train_X[i:i + 1],
                            self.y: train_y[i:i + 1]
                        })

                currentCost = sess.run(
                    cost, feed_dict={
                        self.X: train_X,
                        self.y: train_y
                    })

                print("Epoch = %d, cost = %.5f " % (epoch + 1, currentCost))
                # save the model

            self.saver.save(sess, self.savefile)