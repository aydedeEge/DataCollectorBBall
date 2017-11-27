class PlayerInput:
    
    def setValues(self, cScore, gScore, pID, tID):
        self.careerScore = cScore
        self.gameScore = gScore
        self.playerID = pID
        self.teamID = tID

    def toString(self):
        return "Player " + str(self.playerID) + ", on team " + str(self.teamID) + ", with career score " +\
        str(self.careerScore) + ", had game score " + str(self.gameScore)
    
    def __init__(self):
        self.careerScore = 0
        self.gameScore = 0
        self.playerID = 0
        self.teamID = 0
