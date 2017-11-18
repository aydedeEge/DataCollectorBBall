import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split

from input.dbRawInput import (dbInit, getmatchIDsValid, getPlayerScores,
                              getPlayerScoresForMatches)
from model.playerInput import PlayerInput
from pathlib import Path

MAX_PLAYER_PER_TEAM = 5
# Highest score found in db is 48.something
NORMALIZING_SCORE_UPPER_BOUND = 50.0
# transform an array of players


def getInputArrayFromPlayers(playersArray):
    inputArray = []
    for player in playersArray:
        inputArray.append(player.careerScore)
    return inputArray


def getAverageAndDistributionVar(inputArray):
    average = np.mean(inputArray)
    distribution = np.var(inputArray)
    return average, distribution


def normalizeInputArray(inputArray):
    normalizedInput = []
    for score in inputArray:
        normalizedInput.append(score / NORMALIZING_SCORE_UPPER_BOUND)
    return normalizedInput


def get_first(predicate, seq):
    for i in seq:
        if predicate(i):
            return i
    return None


def getNormalizedTeamsPos(playerArray):

    team1 = filter(lambda player: player.teamID == 1, playerArray)
    team2 = filter(lambda player: player.teamID == 2, playerArray)
   
    # sort in order of importance, will cut the last ones in the list
    team1 = sorted(team1, key=lambda player: player.careerScore, reverse=True)
    team2 = sorted(team2, key=lambda player: player.careerScore, reverse=True)
    print("team1")
    for player in team1:
        print(player.toString())
    print("team2")
    for player in team2:
        print(player.toString())
    team1Pos = []
    team2Pos = []
    #this is awfull
    for player in team1:
        print(str(player.inputOrder), str(player.inputOrder == 0), str(len(team1Pos)))
        if(player.inputOrder == 0 and len(team1Pos) < 1):
            team1Pos.append(player)
        elif(player.inputOrder == 1 and len(team1Pos) < 2):
            team1Pos.append(player)
        elif(player.inputOrder == 2 and len(team1Pos) < 3):
            team1Pos.append(player)
        elif(player.inputOrder == 1 and len(team1Pos) < 4):
            team1Pos.append(player)
        elif(player.inputOrder == 2 and len(team1Pos) < 5):
            team1Pos.append(player)
        elif(len(team1Pos) > 3):
            break


    for player in team2:
        if(player.inputOrder == 0 and len(team2Pos) < 1):
            team2Pos.append(player)
        elif(player.inputOrder == 1 and len(team2Pos) < 2):
            team2Pos.append(player)
        elif(player.inputOrder == 2 and len(team2Pos) < 3):
            team2Pos.append(player)
        elif(len(team2Pos) > 3):
            break
    print(team1Pos)
    print(team2Pos)
    return team1Pos, team2Pos


def getNormalizedTeams(playerArray, lambdaPlayerSorting):
    team1 = filter(lambda player: player.teamID == 1, playerArray)
    team2 = filter(lambda player: player.teamID == 2, playerArray)
    # sort in order of importance, will cut the last ones in the list
    team1 = sorted(team1, key=lambdaPlayerSorting, reverse=True)
    team2 = sorted(team2, key=lambdaPlayerSorting, reverse=True)
    # truncate last layers
    team1 = team1[:MAX_PLAYER_PER_TEAM]
    team2 = team2[:MAX_PLAYER_PER_TEAM]

    return team1, team2


def getOrderedPlayersInput(playerArray):
    sortedPlayerArray = sorted(
        playerArray, key=lambda player: player.inputOrder)
    return sortedPlayerArray


def storeDataFormattedAverage():
    dbInit()
    validMatchId = getmatchIDsValid()
    inputSize = MAX_PLAYER_PER_TEAM * 2

    numberOfInputs = len(validMatchId)
    print(numberOfInputs)
    matchesArrayScores = []
    arrayOuput = []
    i = 0
    a = getPlayerScoresForMatches(validMatchId)

    # Very slow, only to try, would need to be improve for real training
    for matchID in validMatchId:
        # try:
        result = a[1][str(matchID)]
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
        arrayOuput.append([result])
    # except Exception as e:
        #     print("nope")

        print("fetch match num", i)
        i = i + 1

    X = np.array(matchesArrayScores)
    y = np.array(arrayOuput)
    # # USE THIS TO SAVE DATA
    np.save('XScoresAverage', X)
    np.save('yMatchesAverage', y)


def storeDataFormatted(sortingPlayers):
    dbInit()
    validMatchId = getmatchIDsValid()
    inputSize = MAX_PLAYER_PER_TEAM * 2

    numberOfInputs = len(validMatchId)
    print(numberOfInputs)
    matchesArrayScores = []
    arrayOuput = []
    i = 0
    a = getPlayerScoresForMatches(validMatchId)

    # Very slow, only to try, would need to be improve for real training
    for matchID in validMatchId:
        # try:
        result = a[1][str(matchID)]
        teams = getNormalizedTeams(
            a[0][str(matchID)], sortingPlayers)
        matchArrayScores = normalizeInputArray(
            getInputArrayFromPlayers(teams[0] + teams[1]))

        if(len(matchArrayScores) == inputSize):
            matchesArrayScores.append(matchArrayScores)
            arrayOuput.append([result])
    # except Exception as e:
        #     print("nope")

        print("fetch match num", i)
        i = i + 1

    X = np.array(matchesArrayScores)
    y = np.array(arrayOuput)
    # # USE THIS TO SAVE DATA
    np.save('XScores', X)
    np.save('yMatches', y)


def storeDataFormattedPosition():
    dbInit()
    validMatchId = getmatchIDsValid()

    numberOfInputs = len(validMatchId)
    print(numberOfInputs)
    matchesArrayScores = []
    arrayOuput = []
    i = 0
    a = getPlayerScoresForMatches(validMatchId)

    # Very slow, only to try, would need to be improve for real training
    for matchID in validMatchId:
        try:
            result = a[1][str(matchID)]
            teams = getNormalizedTeamsPos(a[0][str(matchID)])

            matchArrayScores = normalizeInputArray(
                getInputArrayFromPlayers(teams[0] + teams[1]))

            if(len(matchArrayScores) == 6):
                matchesArrayScores.append(matchArrayScores)
                arrayOuput.append([result])
        except Exception as e:
            print("nope")

        print("fetch match num", i)
        i = i + 1

    X = np.array(matchesArrayScores)
    y = np.array(arrayOuput)
    # # USE THIS TO SAVE DATA
    np.save('XScoresPosition', X)
    np.save('yMatchesPosition', y)


def getDataFormatted(sortingPlayers):
    my_file = Path('XScores.npy')
    if not my_file.is_file():
        storeDataFormatted(sortingPlayers)
    
    X = np.load('XScores.npy')
    y = np.load('yMatches.npy')
    print(X)
    print(y)
    return X, y.flatten()


def getAverageAndDistribution():
     my_file = Path('XScoresAverage.npy')
    if not my_file.is_file():
        storeDataFormattedAverage()
   
    X = np.load('XScoresAverage.npy')
    y = np.load('yMatchesAverage.npy')
    return X, y.flatten()


def getDataPositionOrder():
    
    my_file = Path('XScoresPosition.npy')
    if not my_file.is_file():
        storeDataFormattedPosition()
    X = np.load('XScoresPosition.npy')
    y = np.load('yMatchesPosition.npy')

    return X, y.flatten()


def getSortedOrder():
    return getDataFormatted(lambda player: player.careerScore)
