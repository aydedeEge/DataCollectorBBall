import MySQLdb
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from model.playerInput import PlayerInput
from load_config import read_config, set_env_vars


def dbInit():
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)


def getmatchIDsValid():
    connection = MySQLdb.connect(host=os.environ["host"],    # your host, usually localhost
                                 # your username
                                 user=os.environ["user"],
                                 passwd=os.environ["pwd"],  # your password
                                 db=os.environ["db"])        # name of the data base

    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT  distinct match_id FROM d2matchb_bball.player_matches where match_id is not null and score is not null;")
    result_set = cursor.fetchall()
    matchId = []
    for row in result_set:
        matchId.append(row["match_id"])
    return matchId

def getSeasonYearFromDate(date):
    items = str(date).split("-")
    if(int(items[1]) > 4):
        return items[0]
    else:
        return int(items[0]) - 1

#this method takes in a bunch of match IDs and returns the following:
# a dictionary of LISTS of playerInputs where the key to each list is the match ID
# a dictionary of VALUES of outputs (W or L) where the key to each value is the match ID
def getPlayerScoresForMatches(match_ids):
    connection = MySQLdb.connect(host=os.environ["host"],
                                 user=os.environ["user"],
                                 passwd=os.environ["pwd"],
                                 db=os.environ["db"])
    #cursor for our connection
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)

    #we want to fetch all match IDs together so we append with OR in between
    match_or_condition = "match_id = "
    for m_id in match_ids:
        match_or_condition += str(m_id) + ' OR match_id ='
    match_or_condition = match_or_condition[:-14]

    #make the command and execute
    command = "SELECT * FROM d2matchb_bball.player_matches where " + match_or_condition + ";"
    cursor.execute(command)
    player_matches_result_set = cursor.fetchall()

    #first we just get the player IDs so we can go get the career stats in bulk.
    player_ids = []
    for row in player_matches_result_set:
        curr_player_id = str(getSeasonYearFromDate(row["mdate"])) + str(row["pid"])
        if(curr_player_id not in player_ids):
            player_ids.append(curr_player_id)

    #now we can get the career stats in bulk, since we have all the player IDs
    player_career_stats = {}
    player_career_pos = {}
    player_id_or_condition = "player_stats_id = "
    for player_id in player_ids:
        player_id_or_condition += player_id + " OR player_stats_id ="
    player_id_or_condition = player_id_or_condition[:-21]

    #complete and execute command
    command = "SELECT * FROM player_stats where " + player_id_or_condition + ";"
    cursor.execute(command)
    player_stats_result_set = cursor.fetchall()

    # for each row, we have a career stat
    for row in player_stats_result_set:
        player_career_stats[str(row["player_stats_id"])] = row["score"]
        player_career_pos[str(row["player_stats_id"])] = row["position"]


    #now we can make the final player objects
    game_results = {} # all of the results of the game (W or L)
    player_inputs = {} # all of the player inputs (dictionary of lists)
    for row in player_matches_result_set:
        home_away = row["home_away"]
        match_id = str(row["match_id"])
        if(match_id not in game_results): #if we haven't updated this output
            if((row["winloss"] == "W" and home_away == "H") or (row["winloss"] == "L" and home_away == "A")):
                game_results[match_id] = 1
            else:
                game_results[match_id] = 0
        game_score = row["score"]
        if(game_score is None):
            print("Warning: game score was none for player_match_id = " + str(row["player_match_id"]) +\
                ", consider running the player_match_scores.py for this id")
        # TODO fetch the position string once we get it
        position = ""
        if home_away == "H":
            team_id = 1
        else:
            team_id = 2
        career_score = player_career_stats[str(getSeasonYearFromDate(row["mdate"])) + str(row["pid"])]
        
        position = player_career_pos[str(getSeasonYearFromDate(row["mdate"])) + str(row["pid"])]
        print(career_score)
        print(position)
        player = PlayerInput()
        player.setValues(cScore=career_score, gScore=game_score,
                             pID=str(row["pid"]), tID=team_id, position=position)
        if(match_id not in player_inputs):
            player_inputs[match_id] = []
        player_inputs[match_id].append(player)

    #for mi in player_inputs:
    #    for pi in player_inputs[mi]:
    #        print(pi.toString())

    return player_inputs, game_results

# returns [0] = array of players ofbooth team for this match
#        [1] = team winner, 1 if home team won, 0 if lost

def getPlayerScores(match_id):

    connection = MySQLdb.connect(host=os.environ["host"],    # your host, usually localhost
                                 # your username
                                 user=os.environ["user"],
                                 passwd=os.environ["pwd"],  # your password
                                 db=os.environ["db"])        # name of the data base

    # you must create a Cursor object. It will let
    # you execute all the queries you need
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)

    # I want to take in a Match ID.
    # From that Match ID, I want to get all of the players who played in that match
    # and their CAREER (not match) scores at that point.
    # since we don't have matchID in player matches, that could be the first step.
    cursor.execute(
        "SELECT * FROM d2matchb_bball.player_matches where match_id = '" + str(match_id) + "';")
    result_set = cursor.fetchall()
    # This returns player IDs and scores on the first team, player IDs and scores on the second team
    # the winning team and all of the players' career stats at that point
    playerInputs = []
    output = -1
    for row in result_set:
        home_away = row["home_away"]
        if(output == -1):
            if((row["winloss"] == "W" and home_away == "H") or (row["winloss"] == "L" and home_away == "A")):
                output = 1
            else:
                output = 0
        gScore = row["score"]
        pID = row["pid"]
        # TODO fetch the position string once we get it
        
        if(home_away == "H"):
            tID = 1
        else:
            tID = 2
        pStatsID = getSeasonYearFromDate(row["mdate"]) + str(pID)
        cursor.execute(
            "SELECT * FROM player_stats where player_stats_id = " + pStatsID + ";")
        cScore = cursor.fetchall()[0]["score"]
        position = cursor.fetchall()[0]["position"]
        print(position)
        currPlayer = PlayerInput()
        currPlayer.setValues(cScore=cScore, gScore=gScore,
                             pID=pID, tID=tID, position=position)
        playerInputs.append(currPlayer)

    # for pi in playerInputs:
    #     print(pi.toString())

    return playerInputs, output

if __name__ == '__main__':
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)
    #matchIDs = getmatchIDsValid()
    #for m in matchIDs:
    #    print(m)
    matches = ["46673", "46633", "46675"]
    getPlayerScoresForMatches(matches)
