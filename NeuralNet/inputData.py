from sklearn import datasets
import numpy as np
import os,sys,inspect
import MySQLdb
from sklearn.model_selection import train_test_split

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
RANDOM_SEED = 42


#TODO import data from database

def getInputData():
    
    iris = datasets.load_iris()
    data = iris["data"]
    target = iris["target"]

    # Prepend the column of 1s for bias
    N, M = data.shape
    all_X = np.ones((N, M + 1))
    all_X[:, 1:] = data

    # Convert into one-hot vectors
    num_labels = len(np.unique(target))
    all_Y = np.eye(num_labels)[target]  # One liner trick!
    return train_test_split(all_X, all_Y, test_size=0.33, random_state=RANDOM_SEED)

def getPlayerScores():
    connection = MySQLdb.connect(host = os.environ["host"],    # your host, usually localhost
                                 user = os.environ["user"],         # your username
                                 passwd = os.environ["pwd"],  # your password
                                 db = os.environ["db"])        # name of the data base

    # you must create a Cursor object. It will let
    # you execute all the queries you need
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)

    # I want to take in a Match ID.
    # From that Match ID, I want to get all of the players who played in that match
    # and their CAREER (not match) scores at that point.
    # since we don't have matchID in player matches, that could be the first step. 
    cursor.execute("SELECT * FROM player_stats")
    result_set = cursor.fetchall()