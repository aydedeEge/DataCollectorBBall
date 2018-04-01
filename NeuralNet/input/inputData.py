import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split

from input.dbRawInput import (dbInit, getmatchIDsValid, getPlayerScores,
                              getPlayerScoresForMatches, getMatchScores,
                              getMatchesOnDay)
from model.playerInput import PlayerInput
from model.team import Team
import math
from pathlib import Path

MAX_PLAYER_PER_TEAM = 7
MAX_PLAYER_PER_POS_TEAM = 5
#Career score, short score, standard deviation
NORMALIZE_UPPER_BOUNDS = (50.0, 65.0, 25.0)
# transform an array of players
# create a score (float) array, usable by a neural net, from an array of players
def getInputArrayFromPlayers(playersArray):
    inputArray = []
    outputArray = []
    for player in playersArray:
        inputArray.append(player.careerScore)
        inputArray.append(player.shortScore)
        inputArray.append(player.stdev_10)
        outputArray.append(player.gameScore)
    return inputArray, outputArray


def getAverageAndDistributionVar(inputArray):
    average = np.mean(inputArray)
    distribution = np.var(inputArray)
    return [average, distribution]


def normalizeInputArray(inputArray):
    normalizedInput = []
    count = 0
    for score in inputArray:
        normalizedInput.append(score / NORMALIZE_UPPER_BOUNDS[count % len(NORMALIZE_UPPER_BOUNDS)])
        count +=1
    return normalizedInput


def getNormalizedTeamsPos(playerArray):

    playerOfteam1 = filter(lambda player: player.teamID == 1, playerArray)
    playerOfteam2 = filter(lambda player: player.teamID == 2, playerArray)

    # sort in order of importance, will cut the last ones in the list
    playerOfteam1 = sorted(
        playerOfteam1, key=lambda player: player.careerScore, reverse=True)
    playerOfteam2 = sorted(
        playerOfteam2, key=lambda player: player.careerScore, reverse=True)

    team1 = Team()
    team1.setValues(playerOfteam1)
    team2 = Team()
    team2.setValues(playerOfteam2)
    return team1.positionArray, team2.positionArray

# unused
def getNormalizedTeams(playerArray):
    print("This method is unused. You shouldn't get here.")
    team1 = filter(lambda player: player.teamID == 1, playerArray)
    team2 = filter(lambda player: player.teamID == 2, playerArray)
    # sort in order of importance, will cut the last ones in the list
    team1 = sorted(team1, key=lambda player: player.careerScore, reverse=True)
    team2 = sorted(team2, key=lambda player: player.careerScore, reverse=True)
    # truncate last layers
    team1 = team1[:MAX_PLAYER_PER_TEAM]
    team2 = team2[:MAX_PLAYER_PER_TEAM]

    return team1, team2


def getOrderedPlayersInput(playerArray):
    sortedPlayerArray = sorted(
        playerArray, key=lambda player: player.inputOrder)
    return sortedPlayerArray


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def normalizeResult(pointsHome, pointsAway):
    # diff = float(pointsHome - pointsAway) / 10.0
    # diffScaled = sigmoid(diff)
    # pHome = diffScaled
    # pAway = 1 - diffScaled
    pHome = 0
    pAway = 0
    if pointsHome > pointsAway:
        pHome = 1
    else:
        pAway = 1
    return pHome, pAway


def storeDataFormatted(numInputPerTeam, getNormalizeTeamsFun, x_path, y_path):
    dbInit()
    validMatchId = getmatchIDsValid()
    # test = [
    #     validMatchId[0], validMatchId[10], validMatchId[20], validMatchId[30],
    #     48652, 48353
    # ]
    #validMatchId = test
    inputSize = numInputPerTeam * 2
    numberOfInputs = len(validMatchId)
    print(numberOfInputs)

    matchesArrayScores = []
    arrayOuput = []
    #results getMatchScores(validMatchId)
    #print(results)
    player_inputs, matches_on_day = getPlayerScoresForMatches(validMatchId)
    day_index = -1

    for day in matches_on_day:
        match_ids = matches_on_day[day]
        matchesArrayScores.append([])
        arrayOuput.append([])
        day_index += 1
        for matchID in match_ids:
            try:
                teams = getNormalizeTeamsFun(player_inputs[str(matchID)])
                inputArray, result = getInputArrayFromPlayers(
                    teams[0] + teams[1])

                matchArrayScores = normalizeInputArray(inputArray)

                if (len(matchArrayScores) == inputSize):
                    matchesArrayScores[day_index].append(matchArrayScores)
                    arrayOuput[day_index].append(result)
                else:
                    print("not enough player : ", len(matchArrayScores),
                          "in match ", matchID)

            except Exception as e:
                print(e)

    X = np.array(matchesArrayScores)
    y = np.array(arrayOuput)
    # # USE THIS TO SAVE DATA
    np.save(x_path, X)
    np.save(y_path, y)
    #TODO: check out bcolz to save or load


def getDataPositionOrder():
    x_path = 'XScoresPos.npy'
    y_path = 'yMatchesPos.npy'
    my_file = Path(x_path)
    if not my_file.is_file():
        #number of inputs is 21, since 7 players with 3 stats each (career, short, stdev)
        storeDataFormatted(21, getNormalizedTeamsPos, x_path, y_path)
    X = np.load(x_path)
    y = np.load(y_path)
    return X, y

#unused
def getSortedOrder():
    print("THIS METHOD SHOULD NOT BE BEING CALLED!")
    x_path = 'XScores.npy'
    y_path = 'yMatches.npy'
    my_file = Path(x_path)
    if not my_file.is_file():
        storeDataFormatted(MAX_PLAYER_PER_TEAM * 2, getNormalizedTeams, x_path,
                           y_path)
    X = np.load(x_path)
    y = np.load(y_path)
   
    return X, y

# unused
def getSortedOrderForDay(day):
    print("THIS METHOD IS UNUSED. WHY IS IT BEING CALLED?")
    dbInit()
    inputSize = MAX_PLAYER_PER_POS_TEAM * 2
    matchesArrayScores = []
    arrayOuput = []
    validMatchId = getMatchesOnDay(day)
    player_inputs, matches_on_day = getPlayerScoresForMatches(validMatchId)
    gamesPlayer = []
    for matchID in validMatchId:
        try:
            teams = getNormalizedTeamsPos(
                player_inputs[str(matchID)])
            gamePlayers = teams[0] + teams[1]
            gamesPlayer.append(gamePlayers)
            inputArray, result = getInputArrayFromPlayers(gamePlayers)

            matchArrayScores = normalizeInputArray(inputArray)
           
            if(len(matchArrayScores) == inputSize):
                matchesArrayScores.append(matchArrayScores)
                arrayOuput.append(result)
            else:
                print("not enough player : ", len(
                    matchArrayScores), "in match ", matchID)

        except Exception as e:
            print("matchID:",matchID ," failed")
   
    X = np.array(matchesArrayScores)
    y = np.array(arrayOuput)
    return X,y,gamesPlayer

# def getSortedOrderForDay(day):
#     dbInit()
#     inputSize = MAX_PLAYER_PER_TEAM * 4
#     matchesArrayScores = []
#     arrayOuput = []
#     validMatchId = getMatchesOnDay(day)
#     player_inputs, matches_on_day = getPlayerScoresForMatches(validMatchId)

#     for matchID in validMatchId:
#         try:
#             teams = getNormalizedTeamsPos(player_inputs[str(matchID)])
#             inputArray, result = getInputArrayFromPlayers(teams[0] + teams[1])

#             matchArrayScores = normalizeInputArray(inputArray)

#             if (len(matchArrayScores) == inputSize):

#                 matchesArrayScores.append(matchArrayScores)
#                 arrayOuput.append(result)
#             else:
#                 print(len(matchArrayScores))
#                 print("not enough player : ", len(matchArrayScores),
#                       "in match ", matchID)

#         except Exception as e:
#             print("matchID:", matchID, " failed")

#     X = np.array(matchesArrayScores)
#     y = np.array(arrayOuput)
#     return X, y




def getInputForDay(day):
    dbInit()
    inputSize = MAX_PLAYER_PER_TEAM * 6 # career stats, short term stats, variance
    matchesArrayScores = []
    validMatchId = getMatchesOnDay(day)
    player_inputs, matches_on_day = getPlayerScoresForMatches(validMatchId)
    playerList = []
    for matchID in validMatchId:
        #try:
        teams = getNormalizedTeamsPos(player_inputs[str(matchID)])
        inputArray, result = getInputArrayFromPlayers(teams[0] + teams[1])
        
        matchArrayScores = normalizeInputArray(inputArray)

        if (len(matchArrayScores) == inputSize):
            playerList = playerList + teams[0] + teams[1]
            matchesArrayScores.append(matchArrayScores)
        else:
            print(len(matchArrayScores))
            print("not enough player : ", len(matchArrayScores),
                    "in match ", matchID)

        #except Exception as e:
        #    print("matchID:", matchID, " failed")

    X = np.array(matchesArrayScores)

    return X, playerList


def getStat():
    dbInit()
    validMatchId = getmatchIDsValid()
    # validMatchId = [validMatchId[8],validMatchId[7],validMatchId[4],validMatchId[5]]
    numberOfInputs = len(validMatchId)
    results = getMatchScores(validMatchId)
    matchesTeams = getPlayerScoresForMatches(validMatchId)
    return matchesTeams, validMatchId, results
