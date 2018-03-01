class Team:

    def setValues(self, players):
        self.players = players
        for player in players:
            #print(player.toString())
            self.positionDict[str(player.inputOrder)].append(player)

        playerC = self.positionDict['0'][0]
        playerF = self.positionDict['1'][0]
        playerG = self.positionDict['2'][0]
        #secondPlayerC = self.positionDict['0'][1]
        secondPlayerF = self.positionDict['1'][1]
        secondPlayerG = self.positionDict['2'][1]
        self.positionArray.append(playerC) #Add the center
        self.positionArray.append(playerF) #Add the Forward
        self.positionArray.append(playerG) #Add the Guard
        self.positionArray.append(secondPlayerG)
        self.positionArray.append(secondPlayerF)

    def __init__(self):
        self.positionDict = {'0': [], '1': [], '2': [], '3': []}
        self.positionArray = []
        self.players = []
