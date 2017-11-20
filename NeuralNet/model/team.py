class Team:
    def setValues(self, players):
        for player in players:
            self.positionDict[str(player.inputOrder)].append(player)
        playerC = self.positionDict['0'][0]
        playerF = self.positionDict['1'][0]
        playerG = self.positionDict['2'][0]
        print(playerC.toString())
        print(playerF.toString())
        print(playerG.toString())
        self.positionArray.append(playerC) #Add the center 
        self.positionArray.append(playerF) #Add the Forward
        self.positionArray.append(playerG) #Add the Guard
 

    def __init__(self):
        self.positionDict = {'0':[],'1':[],'2':[]}
        self.positionArray = []