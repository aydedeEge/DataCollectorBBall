import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split

from input.dbRawInput import (
    dbInit, getmatchIDsValid, getPlayerScores, getPlayerScoresForMatches, getMatchScores)
from model.playerInput import PlayerInput
from model.team import Team
import math
from pathlib import Path

MAX_PLAYER_PER_TEAM = 7
# Highest score found in db is 48.something
NORMALIZING_SCORE_UPPER_BOUND = 50.0

# transform an array of players
# create a score (float) array, usable by a neural net, from an array of players


def getInputArrayFromPlayers(playersArray):
    inputArray = []
    for player in playersArray:
        inputArray.append(player.careerScore)
    return inputArray


def getAverageAndDistributionVar(inputArray):
    average = np.mean(inputArray)
    distribution = np.var(inputArray)
    return [average, distribution]


def normalizeInputArray(inputArray):
    normalizedInput = []
    for score in inputArray:
        normalizedInput.append(score / NORMALIZING_SCORE_UPPER_BOUND)
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


def getNormalizedTeams(playerArray):
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
    diff = float(pointsHome - pointsAway) / 10.0
    diffScaled = sigmoid(diff)
    pHome = diffScaled
    pAway = 1 - diffScaled
    
    return pHome, pAway

def storeDataFormattedAverage():
    dbInit()
    validMatchId = getmatchIDsValid()
    inputSize = MAX_PLAYER_PER_TEAM * 2

    numberOfInputs = len(validMatchId)
    matchesArrayScores = []
    arrayOuput = []
    i = 0
    results = getMatchScores(validMatchId)

    a = getPlayerScoresForMatches(validMatchId)

    # Very slow, only to try, would need to be improve for real training
    for matchID in validMatchId:
        try:
            result = normalizeResult(
                results[str(matchID)][0], results[str(matchID)][1])
            print(result)
            teams = getNormalizedTeams(
                a[0][str(matchID)], lambda player: player.inputOrder)

            scoresTeam1Average, scoresTeam1Var = getAverageAndDistributionVar(
                normalizeInputArray(getInputArrayFromPlayers(teams[0])))

            scoresTeam2Average, scoresTeam2Var = getAverageAndDistributionVar(
                normalizeInputArray(getInputArrayFromPlayers(teams[1])))

            matchArrayScores = [scoresTeam1Average,
                                scoresTeam1Var, scoresTeam2Average, scoresTeam2Var]
            print(matchArrayScores)

            matchesArrayScores.append(matchArrayScores)
            arrayOuput.append(result)
        except Exception as e:
            print("nope")

        print("fetch match num", i)
        i = i + 1

    X = np.array(matchesArrayScores)
    y = np.array(arrayOuput)
    # # USE THIS TO SAVE DATA
    np.save('XScoresAverage', X)
    np.save('yMatchesAverage', y)


def storeDataFormatted(numInputPerTeam, getNormalizeTeamsFun,x_path, y_path):
    dbInit()
    validMatchId = getmatchIDsValid()
    # test = [validMatchId[0], validMatchId[10], validMatchId[20], validMatchId[30]]
    # validMatchId = test
    inputSize = numInputPerTeam * 2
    numberOfInputs = len(validMatchId)
    print(numberOfInputs)

    matchesArrayScores = []
    arrayOuput = []
    results = getMatchScores(validMatchId)
    print(results)
    matchesTeams = getPlayerScoresForMatches(validMatchId)

    for matchID in validMatchId:
        try:
            result = normalizeResult(
                results[str(matchID)][0], results[str(matchID)][1])
            print(result)

            teams = getNormalizeTeamsFun(
                matchesTeams[0][str(matchID)])
            matchArrayScores = normalizeInputArray(
                getInputArrayFromPlayers(teams[0] + teams[1]))

            if(len(matchArrayScores) == inputSize):
                matchesArrayScores.append(matchArrayScores)
                arrayOuput.append(result)
            else:
                print("not enough player : ", len(
                    matchArrayScores), "in match ", matchID)

        except Exception as e:
            print("no")

    X = np.array(matchesArrayScores)
    y = np.array(arrayOuput)
    # # USE THIS TO SAVE DATA
    np.save(x_path, X)
    np.save(y_path, y)


def getAverageAndDistribution():
    my_file = Path('XScoresAverage.npy')
    if not my_file.is_file():
        storeDataFormattedAverage()

    X = np.load('XScoresAverage.npy')
    y = np.load('yMatchesAverage.npy')

    print(y)
    return X, y


def getDataPositionOrder():
    x_path = 'XScoresPos.npy'
    y_path = 'yMatchesPos.npy'
    my_file = Path(x_path)
    if not my_file.is_file():
        storeDataFormatted(5, getNormalizedTeamsPos, x_path, y_path)
    X = np.load(x_path)
    y = np.load(y_path)
    return X, y


def getSortedOrder():
    x_path = 'XScores.npy'
    y_path = 'yMatches.npy'
    my_file = Path(x_path)
    if not my_file.is_file():
        storeDataFormatted(MAX_PLAYER_PER_TEAM, getNormalizedTeams, x_path, y_path)
    X = np.load(x_path)
    y = np.load(y_path)
    print(y)
    return X, y
