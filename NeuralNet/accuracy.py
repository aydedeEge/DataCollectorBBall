from System3.ilp import ilp
from model.team import PLAYER_POSITIONS
import numpy as np

GLOBAL_BUDGET = 60000
DEFAULT_COST = 4000

def compute_accuracy(games_predicted, games_actual, returnLineup):
    predictedScores = [item for items in games_predicted for item in items]
    actualScores = [item for items in games_actual for item in items]
    position_array = []
    for game in games_predicted:
        position_array.extend(PLAYER_POSITIONS)
    playerCosts = np.full(len(predictedScores), DEFAULT_COST)

    index_players_predicted = ilp(predictedScores, playerCosts, position_array,
                                  GLOBAL_BUDGET)
    index_players_actual = ilp(actualScores, playerCosts, position_array,
                               GLOBAL_BUDGET)

    actual_score = sum([actualScores[i] for i in index_players_actual])
    gotten_score = sum([actualScores[i] for i in index_players_predicted])
    if returnLineup:
        return gotten_score / actual_score * 100, index_players_actual, index_players_predicted
    return gotten_score / actual_score * 100


def predict_lineup(playerList):
    predictedScores = [player.expectedScore for player in playerList]
    position_array = []
    #for game in range(int(len(playerList) / len(PLAYER_POSITIONS))):
    #    position_array.extend(PLAYER_POSITIONS)
    for p in playerList:
        if(p.dailyPosition == "SG"):
            position_array.append(2)
        elif(p.dailyPosition == "SF"):
            position_array.append(3)
        elif(p.dailyPosition == "PG"):
            position_array.append(4)
        elif(p.dailyPosition == "PF"):
            position_array.append(5)
        elif(p.dailyPosition == "C"):
            position_array.append(1)
        else:
            print("empty daily position for lineup")
    playerCosts = [player.salary for player in playerList]

    index_players_predicted = ilp(predictedScores, playerCosts, position_array,
                                  GLOBAL_BUDGET)

    selected_lineup = [playerList[i] for i in index_players_predicted]
    expected_score = sum([player.expectedScore for player in selected_lineup])
    return expected_score, selected_lineup
