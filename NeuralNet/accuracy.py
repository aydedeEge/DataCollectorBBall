from System3.ilp import ilp
from model.team import PLAYER_POSITIONS
from model.playerInput import COST
import numpy as np

GLOBAL_BUDGET = 60000

def compute_accuracy(games_predicted, games_actual, returnLineup):
    predictedScores = [item for items in games_predicted for item in items]
    actualScores = [item for items in games_actual for item in items]
    position_array = []
    for game in games_predicted:
        position_array.extend(PLAYER_POSITIONS)
    playerCosts = np.full(len(predictedScores), COST)

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
    for game in range(int(len(playerList) / len(PLAYER_POSITIONS))):
        position_array.extend(PLAYER_POSITIONS)

    playerCosts = [player.salary for player in playerList]

    index_players_predicted = ilp(predictedScores, playerCosts, position_array,
                                  GLOBAL_BUDGET)

    selected_lineup = [playerList[i] for i in index_players_predicted]
    expected_score = sum([player.expectedScore for player in selected_lineup])
    return expected_score, selected_lineup
