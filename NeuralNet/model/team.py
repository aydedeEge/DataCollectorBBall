CENTER = 0
FORWARD = 1
GUARD = 2
TEAM_REQUIREMENTS = {str(CENTER): 1, str(FORWARD): 3, str(GUARD): 3}
PLAYER_POSITIONS = (1, 2, 3, 3, 4, 5, 5, 1, 2, 3, 3, 4, 5, 5)


class Team:
    def setValues(self, players):
        self.players = players
        #Find the centers
        self.findCenters()
        self.findForwardsAndGuards()

        for player in players:

            if player.inputOrder is not None:
                #     print(player.toString())
                self.positionDict[str(player.inputOrder)].append(player)
            else:
                print("player with nothing")
            #might need to sort them TODO
        wantedC = TEAM_REQUIREMENTS[str(CENTER)]
        wantedF = TEAM_REQUIREMENTS[str(FORWARD)]
        wantedG = TEAM_REQUIREMENTS[str(GUARD)]
        haveF = len(self.positionDict['1'])
        haveG = len(self.positionDict['2'])

        playersC = self.positionDict['0'][0:wantedC]
        #the idea here is to substitute a guard with a forward and vice versa if we're short one.
        if(haveF == wantedF - 1 and haveG > wantedG):
            wantedG +=1
        elif(haveG == wantedG - 1 and haveF > wantedF):
            wantedF +=1
        playersF = self.positionDict['1'][0:wantedF]
        playersG = self.positionDict['2'][0:wantedG]

        allPlayers = playersC + playersF + playersG
        self.positionArray = allPlayers

    def findCenters(self):
        filteredC = list(filter(lambda x: x.position == "C", self.players))
        filteredCF = list(filter(lambda x: x.position == "C-F", self.players))
        filteredFC = list(filter(lambda x: x.position == "F-C", self.players))
        if len(filteredC) > 0:
            for center in filteredC:
                center.setInputOrder(CENTER)
            return

        def assignCToLowestShortscore(possibleCenters):
            #find the CF with lowest score, more probable to be real C
            Cplayer = possibleCenters[0]
            for possibleCenter in possibleCenters:
                if possibleCenter.shortScore < Cplayer.shortScore:
                    Cplayer = possibleCenter
            Cplayer.setInputOrder(CENTER)

        if len(filteredCF) > 0:
            assignCToLowestShortscore(filteredCF)
            return
        if len(filteredFC) > 0:
            assignCToLowestShortscore(filteredFC)

    def findForwardsAndGuards(self):
        filteredG = list(filter(lambda x: x.position == "G", self.players))
        filteredF = list(filter(lambda x: x.position == "F", self.players))
        filteredCF = list(
            filter(lambda x: (x.position == "C-F" and x.inputOrder is None),
                   self.players))
        filteredFC = list(
            filter(lambda x: (x.position == "F-C" and x.inputOrder is None),
                   self.players))
        filteredGF = list(filter(lambda x: x.position == "G-F", self.players))
        filteredFG = list(filter(lambda x: x.position == "F-G", self.players))
        #Find required number of guards
        for guard in filteredG:
            guard.setInputOrder(GUARD)
        if len(filteredG) < TEAM_REQUIREMENTS[str(
                GUARD)]:  # needs to add the G-F as guards
            #dont know yet how to find best G-F to add as guards
            missingGuards = TEAM_REQUIREMENTS[str(GUARD)] - len(filteredG)
            if len(filteredG) >= missingGuards:
                for guard in filteredGF[0:missingGuards]:
                    guard.setInputOrder(GUARD)
                    filteredGF.remove(
                        guard)  # cant be used has a forward anymore
            #else there is no point

        #Put the rest as forwards and hope for the best
        for forward in filteredF + filteredCF + filteredFC + filteredGF + filteredFG:
            forward.setInputOrder(FORWARD)

    def __init__(self):
        self.positionDict = {'0': [], '1': [], '2': [], '3': []}
        self.positionArray = []
        self.players = []
