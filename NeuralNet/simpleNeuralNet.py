import numpy as np
import inputData as input

NUM_ITERATION = 1000


def Sigmoid(x):
    return 1 / (1 + np.exp(-x))


def backPropSigmoid(x):
    return x * (1 - x)


def main():
    X = np.array([[0, 0, 1], [0, 1, 1], [1, 0, 1], [1, 1, 1]])
    y = np.array([[0,0,1,1]]).T
    
    weights = 2 * np.random.random((3, 1)) - 1
    print("Initial weights : ",weights)

    for i in xrange(NUM_ITERATION):
   
        layer0 = X
         #-> only need to compute dot product w*input with the sigmoid function(Activation)
        layer1 = Sigmoid(np.dot(layer0,weights))
        
        # compute error
        error = y-layer1
        # print(i," : error =",error)
      
        #<- backpropagation
        l1_delta = error * backPropSigmoid(layer1)

        # update weights
        weights+=np.dot(layer0.T, l1_delta)
    
    print("Output after training")
   print(layer1)
if __name__ == '__main__':
    main()
