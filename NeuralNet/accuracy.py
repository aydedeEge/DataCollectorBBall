from System3.ilp import ilp
import numpy as np

GLOBAL_BUDGET = 60000
COST = 4000


def compute_accuracy(games_predicted, games_actual):
    predictedScores = [item for items in games_predicted for item in items]
    actualScores = [item for items in games_actual for item in items]
    position_array = []
    player_pos = (1, 2, 3, 4, 5, 1, 2, 3, 4, 5)
    for game in games_predicted:
        position_array.extend(player_pos)
    playerCosts = np.full(len(predictedScores), COST)

    index_players_predicted = ilp(predictedScores, playerCosts, position_array,
                                  GLOBAL_BUDGET)
    index_players_actual = ilp(actualScores, playerCosts, position_array,
                               GLOBAL_BUDGET)

    actual_score = sum([actualScores[i] for i in index_players_actual])
    gotten_score = sum([actualScores[i] for i in index_players_predicted])

    return gotten_score / actual_score * 100
