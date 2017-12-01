
import numpy as np
from model.team import Team

from input.inputData import getStat, getNormalizedTeamsPos


class Profile:

    def __init__(self, team):
        self.posDict = {"C": 0, "C-F": 0, "F": 0, "F-C": 0,
                        "F-G": 0, "G": 0, "G-F": 0}
        for player in team.players:
            try:
                self.posDict[player.position] = self.posDict[player.position] + 1

            except Exception as e:
                s = 0


def getTeams(playerArray):

    playerOfteam1 = filter(lambda player: player.teamID == 1, playerArray)
    playerOfteam2 = filter(lambda player: player.teamID == 2, playerArray)

    # sort in order of importance, will cut the last ones in the list
    playerOfteam1 = sorted(
        playerOfteam1, key=lambda player: player.careerScore, reverse=True)
    playerOfteam2 = sorted(
        playerOfteam2, key=lambda player: player.careerScore, reverse=True)

    team1 = Team()
    team1.setValues(playerOfteam1)
    team2 = Team()
    team2.setValues(playerOfteam2)
    return team1, team2


# def profile(team):
#     posDict = {"C": 0, "C-F": 0, "F": 0, "F-C": 0,
#                "F-G": 0, "G": 0, "G-F": 0, "none": 0}
#     for player in team.players:
#         try:
#             posDict[player.position] = posDict[player.position] + 1

#         except Exception as e:
#             posDict["none"] = posDict["none"] + 1
#     return posDict

def profileIsThere(listProfile, profile):
    for i in range(len(listProfile)):
        com = listProfile[i]
        isSame = True
        for key in com.keys():
            if com[key] != profile[key]:
                if (com[key] < 2 and profile[key] < 2):
                    isSame = False
                    break
        if isSame == True:
            return i
    return -1


def printDict(posDict):
    dictToPrint = ""
    for key in posDict.keys():
        dictToPrint += key
        if posDict[key] >= 2:
            dictToPrint += " : >2   "
        else:
            dictToPrint += " : "
            dictToPrint += str(posDict[key])
            dictToPrint += "   "
    return dictToPrint


def main():
    stats = getStat()
    matches = stats[0]
    print(len(matches))
    listProfile = []
    listIndex = []
    for match_id in stats[1]:
        teams = getTeams(matches[0][str(match_id)])
        team1profile = Profile(teams[0]).posDict
        team2profile = Profile(teams[1]).posDict

        indexProfile1 = profileIsThere(listProfile, team1profile)
        print(indexProfile1)
        if indexProfile1 == -1:
            listProfile.append(team1profile)
            listIndex.append(1)
        else:
            listIndex[indexProfile1] = listIndex[indexProfile1] + 1

        indexProfile2 = profileIsThere(listProfile, team2profile)
        print(indexProfile2)
        if indexProfile2 == -1:
            listProfile.append(team2profile)
            listIndex.append(1)
        else:
            listIndex[indexProfile2] = listIndex[indexProfile2] + 1

    for i in range(len(listProfile)):
        print("Count : ",  listIndex[i], " { ", printDict(listProfile[i]), "}")


if __name__ == '__main__':
    main()
