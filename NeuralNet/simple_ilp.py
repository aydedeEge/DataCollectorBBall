from ilp import ilp
import numpy as np
import pandas as pd

GLOBAL_BUDGET = 60000



def compute_accuracy(games_predicted, games_actual):
    predictedScores = [item for items in games_predicted for item in items]
    actualScores = [item for items in games_actual for item in items]
    position_array = []
    player_pos = (1, 2, 3,3, 4, 5,5, 1, 2, 3,3, 4, 5,5)
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


def getFile(input_file):
    players = pd.read_csv(input_file, index_col=12).as_matrix()
   
    
    return players


def main():
    players = getFile('beatEge.csv')
    positions = players[:,1]
    points = players[:,5]
    cost = players[:,7]
    expected_output = []
    games_played = players[:,6]
    print(games_played)
    player_pos =[]
    GLOBAL_BUDGET = 60000
    for positions in positions:
        if(positions == "C"):
            player_pos.append(1)
        elif(positions == "PG"):
            player_pos.append(2)
        elif(positions == "SG"):
            player_pos.append(3)
        elif(positions == "SF"):
            player_pos.append(4)
        elif(positions == "PF"):
            player_pos.append(5)
    for i in range(len(points)):
        expected_output.append(points[i] * games_played[i])

    
    index_players_predicted = ilp(expected_output, cost, player_pos,
                                  GLOBAL_BUDGET)
  
    gotten_score = sum([points[i] for i in index_players_predicted])
   
    for i in index_players_predicted:
        print(i)
        print("pos "+ str(player_pos[i]))
        print(players[i][3])
    print(gotten_score)


if __name__ == '__main__':
    main()
