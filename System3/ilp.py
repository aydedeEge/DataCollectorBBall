import pulp

def ilp(expectedScores, playerCosts, playerPositions, numberOfPlayers, globalBudget):
    # Set up problem as a Linear Programming Maximisation problem.
    my_lp_problem = pulp.LpProblem("My LP Problem", pulp.LpMaximize)

    # Dictionary for decision variables since we need to create them at run time.
    decisionVariables={}

    # Create decision variables for variables x0 to xn and put in dictionary.
    for playerNum in range(0, numberOfPlayers):
        x = "x" 
        x += str(playerNum)
        decisionVariables[x] = pulp.LpVariable(x, lowBound=0, upBound=1, cat='Integer')

    # for key in decisionVariables:
    #     print(key)
    
    my_lp_problem += 4 * decisionVariables['x'] + 3 * decisionVariables['y'], "Z"
    
    # my_lp_problem += 2 * decisionVariables['y'] <= 25 - decisionVariables['x']
    # my_lp_problem += 4 * decisionVariables['y'] >= 2 * decisionVariables['x'] - 8
    # my_lp_problem += decisionVariables['y'] <= 2 * decisionVariables['x'] - 5
    
    my_lp_problem
    my_lp_problem.solve()


    print(pulp.LpStatus[my_lp_problem.status])

    for variable in my_lp_problem.variables():
        print("{} = {}".format(variable.name, variable.varValue))

    print(pulp.value(my_lp_problem.objective))

def main():
    expectedScores = [150,120,300,500,90,80,170,40,200,150]
    playerCosts = [70,65,90,85,90,55,70,20,100,90]
    playerPositions = [1,2,3,4,5,1,2,3,4,5]
    numberOfPlayers = len(expectedScores)
    globalBudget = 500

    ilp(expectedScores, playerCosts, playerPositions, numberOfPlayers, globalBudget)

if __name__ == '__main__':
    main()
