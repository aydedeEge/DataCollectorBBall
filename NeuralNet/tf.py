
import tensorflow as tf
import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split
import input.inputData as input

RANDOM_SEED = 527
tf.set_random_seed(RANDOM_SEED)
NUMBER_OF_HIDDEN_NODES = 256
LEARNING_RATE = 0.02
TEST_SIZE_PERCENT= 0.33

def init_weights(shape):
    #randomo weight init
    weights = tf.random_normal(shape, stddev=0.1)
    return tf.Variable(weights)


def forwardprop(X, w_1, w_2):
    h = tf.nn.sigmoid(tf.matmul(X, w_1))  # The sigma function

    yhat = tf.matmul(h, w_2)  # The varphi function
    
    return yhat


def get_data():
    #choose which type of data to get
    data, target = input.getDataPositionOrder()
    print("Data size : ",str(len(target)))
    print("Input form : ", data[0])
    print("Output form : ", target[0])
    # Add ones as x0 for bias = [1,score1,score2,....,scoren]
    N, M = data.shape
    all_X = np.ones((N, M + 1))
    all_X[:, 1:] = data

    # Convert vectors
    num_labels = len(np.unique(target))
    all_Y = np.eye(num_labels)[target] 

    return train_test_split(all_X, all_Y, test_size=TEST_SIZE_PERCENT, random_state=RANDOM_SEED)


def main():
    train_X, test_X, train_y, test_y = get_data()

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

    # Backward propagation
    cost = tf.reduce_mean( tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=yhat))
    updates = tf.train.GradientDescentOptimizer(LEARNING_RATE).minimize(cost)

    # Run SGD
    sess = tf.Session()
    init = tf.global_variables_initializer()
    sess.run(init)

    for epoch in range(100):
        
        for i in range(len(train_X)):
            sess.run(updates, feed_dict={ X: train_X[i: i + 1], y: train_y[i: i + 1]})

        train_accuracy = np.mean(np.argmax(train_y, axis=1) ==  sess.run(predict, feed_dict={X: train_X, y: train_y}))
       
        test_accuracy = np.mean(np.argmax(test_y, axis=1) == sess.run(predict, feed_dict={X: test_X, y: test_y}))

        print("Epoch = %d, train accuracy = %.2f%%, test accuracy = %.2f%%"
              % (epoch + 1, 100. * train_accuracy, 100. * test_accuracy))
    
    
   
    sess.close()


if __name__ == '__main__':
    main()
