# from sklearn import datasets
#import numpy as np
import os,sys,inspect
import MySQLdb
# from sklearn.model_selection import train_test_split
import PlayerInput

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from load_config import read_config, set_env_vars
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

def getPlayerScores(match_id):
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
    cursor.execute("SELECT * FROM d2matchb_bball.player_matches where match_id = '" + match_id + "';")
    result_set = cursor.fetchall()
    # This returns player IDs and scores on the first team, player IDs and scores on the second team
    # the winning team and all of the players' career stats at that point
    playerInputs = []
    output = -1
    for row in result_set:
        home_away = result_set["home_away"]
        if(output == -1):
            if((result_set["winloss"] == "W" and home_away == "H") or (result_set["winloss"] == "L" and home_away == "A")):
                output = "W"
            else:
                output = "L"
        gScore = result_set["score"]
        pID = result_set["pid"]
        if(home_away == "H"):
            tID = 1
        else:
            tID = 2
        cursor.execute("SELECT * FROM player_stats where player_stats_id = 2016" + str(pID) + ";")
        cScore = cursor.fetchall[0]["score"]
        currPlayer = PlayerInput.PlayerInput(cScore, gScore, pID, tID)
        playerInputs.append(currPlayer)

    for pi in playerInputs:
        print(pi.toString())
    print("Output is a " + output + " for the home team")

if __name__ == '__main__':
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)
    getPlayerScores(49256)