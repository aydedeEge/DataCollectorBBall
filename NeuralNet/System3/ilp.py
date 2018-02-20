import pulp

def getIndecesOfPlayersAtPosition(positionOfInterest, playerPositions):
    indexArray = []
    for i in range(0, len(playerPositions)):
        if(playerPositions[i] == positionOfInterest):
            indexArray.append(i)
    
    return indexArray
    

def ilp(expectedScores, playerCosts, playerPositions, globalBudget):
    # Set up problem as a Linear Programming Maximisation problem.
    my_lp_problem = pulp.LpProblem("My LP Problem", pulp.LpMaximize)
    numberOfPlayers = len(expectedScores)
    # Dictionary for decision variables since we need to create them at run time.
    decisionVariables={}
    noo = {}
    # Create decision variables for variables x0 to xn and put in dictionary.
    for i in range(0, numberOfPlayers):
        x = "x" 
        x += str(i)
        decisionVariables[x] = pulp.LpVariable(x, cat='Binary')
        noo[x] = i

    # Create objective function using the decision variables and the expected scores.
    my_lp_problem += expectedScores[0] * decisionVariables["x" + str(0)], "Z"
    for i in range(1, numberOfPlayers):
        my_lp_problem += my_lp_problem.objective + expectedScores[i] * decisionVariables["x" + str(i)]

    # Constraints:
    # We will have 6 constraints:
    # 1. Number of players in position 1 = 2.
    # 2. Number of players in position 2 = 2.
    # 3. Number of players in position 3 = 2.
    # 4. Number of players in position 4 = 2.
    # 5. Number of players in position 5 = 2.
    # 6. The sum of the cost of each player * corresponding x value <= global budget.

    # Constraints 1 to 5:
    for i in range(1, 6):
        indecesOfPosition = getIndecesOfPlayersAtPosition(i, playerPositions)
        isFirstIteration = True
        for index in indecesOfPosition:
            if(isFirstIteration):
                my_lp_problem += decisionVariables["x" + str(index)] == 2, "Constraint_" + str(i)
                isFirstIteration = False
            else:
                my_lp_problem.constraints["Constraint_" + str(i)] += decisionVariables["x" + str(index)]

    # Constraint 6:
    my_lp_problem += playerCosts[0] * decisionVariables["x" + str(0)] <= globalBudget, "Constraint_6"
    for i in range(1, numberOfPlayers):
        my_lp_problem.constraints["Constraint_6"] += playerCosts[i] * decisionVariables["x" + str(i)]
    
    # Print out objective function, constraints, and all variables with their corresponding ranges.
    # print(my_lp_problem)

    # Solve ILP problem.
    my_lp_problem.solve()

    # Print status of solved problem (i.e. Not Solved, Optimal, Infeasible, Unbounded, or Undefined).
    # print("\n" + "Status: " + pulp.LpStatus[my_lp_problem.status] + "\n")

    # Print out values of all decision variables.
    # print("Decision Variables: ")
    result = []

    for variable in my_lp_problem.variables():
        # print("{} = {}".format(variable.name, variable.varValue))
        if(variable.varValue == 1):
            result.append(noo[variable.name])
        
    # Print final maximised value of the objective function.
    # print("\nFinal Maximised Value of Objective Function: " + str(pulp.value(my_lp_problem.objective)) + "\n")

    return result

def main():
    expectedScores = [150,120,300,500,90,80,170,40,200,150]
    playerCosts = [70,65,90,85,90,55,70,20,100,90]
    playerPositions = [1,2,3,4,5,1,2,3,4,5]
    numberOfPlayers = len(expectedScores)
    globalBudget = 500

    ilp(expectedScores, playerCosts, playerPositions, numberOfPlayers, globalBudget)

if __name__ == '__main__':
    main()
