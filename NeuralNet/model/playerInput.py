class PlayerInput:
    

    def setValues(self, cScore, sScore, gScore, pID, tID, position, eScore=None, sal=1000):
        self.careerScore = cScore
        self.shortScore = sScore
        self.gameScore = gScore
        self.expectedScore = eScore
        self.playerID = pID
        self.teamID = tID
        self.position = position
        self.inputOrder = self.positionToIndex(self.position)
        self.salary = sal
    
    #return the index of the player in the match array [ powerforwardTeam1 , smallForwardTeam1, ..., powerForwardTeam2, ...]
    #For example, the smallForward of team 1 will return 1
    #To be improve
    def positionToIndex(self,position):
        if((position == "C") or (position == "C-F")):
            return 0
        elif((position == "F") or position == "F-C" or position == "F-G" or position == "G-F"):
            return 1
        elif(position == "G"):
            return 2
        else :
            return 3
  
    def toString(self):
        return "Player " + str(self.playerID) + ", on team " + str(self.teamID) + ", with career score " +\
        str(self.careerScore) + ", had game score " + str(self.gameScore) + "at the position " + self.position + "  .Input order :" + str(self.inputOrder)
    

    def __init__(self):
        self.careerScore = 0
        self.shortScore = 0
        self.gameScore = 0
        self.playerID = 0
        self.teamID = 0
        self.position = ""