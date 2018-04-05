class PlayerInput:
    def setValues(self,
                  cScore,
                  sScore,
                  stdev_10,
                  gScore,
                  pID,
                  tID,
                  position,
                  sal,
                  dpos,
                  eScore=None):
        self.careerScore = cScore
        self.shortScore = sScore
        self.stdev_10 = stdev_10
        self.gameScore = gScore
        self.expectedScore = eScore
        self.playerID = pID
        self.teamID = tID
        self.position = position
        self.salary = sal
        self.dailyPosition = dpos

    #0 = Center, 1=Forward, 2=Guard
    def setInputOrder(self, inputPosition):
        if (self.inputOrder is not None):
            print("change Assigned from" + str(self.inputOrder) + " to " +
                  str(inputPosition))

        self.inputOrder = inputPosition

    def toString(self):
        # return "Player " + str(self.playerID) + ", on team " + str(self.teamID) + ", with career score " +\
        # str(self.careerScore) + ", had game score " + str(self.gameScore) + "at the position " + self.position + "  .Input order :" + str(self.inputOrder)
        return "Player " + str(self.playerID) + ", on team " + str(
            self.teamID
        ) + ",  position " + self.position + "  .Expected score :" + str(
            self.expectedScore) + " .STDEV: " + str(self.stdev_10)

    def __init__(self):
        self.careerScore = 0
        self.shortScore = 0
        self.stdev_10 = 0
        self.gameScore = 0
        self.playerID = 0
        self.teamID = 0
        self.position = ""
        self.inputOrder = None