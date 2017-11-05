
class Player:

    def __init__(self, Name, Season, ID, GamesPlayed=None, MinutesPlayed=None, Points=None,
                 FieldGoalsMade=None, FieldGoalsAttempted=None, FieldGoalPercentage=None,
                 ThreeMade=None, ThreeAttempted=None, ThreePercentage=None,
                 FreeThrowsMade=None, FreeThrowsAttempted=None, FreeThrowsPercentage=None,
                 OffRebounds=None, DefRebounds=None, Rebounds=None,
                 Assists=None, Steals=None, Blocks=None, Turnovers=None, Efficiency=None,PersonalFouls=None):
        self.Name = Name
        self.Season = Season
        self.psID = Season + ID
        self.ID = ID
        self.GamesPlayed = float(GamesPlayed)
        self.MinutesPlayed = float(MinutesPlayed)
        self.Points = self.toThirtySix(Points)
        self.FieldGoalsMade = self.toThirtySix(FieldGoalsMade)
        self.FieldGoalsAttempted = self.toThirtySix(FieldGoalsAttempted)
        self.FieldGoalPercentage = self.toThirtySix(FieldGoalPercentage)
        self.ThreeAttempted = self.toThirtySix(ThreeAttempted)
        self.ThreeMade = self.toThirtySix(ThreeMade)
        self.ThreePercentage = self.toThirtySix(ThreePercentage)
        self.FreeThrowsMade = self.toThirtySix(FreeThrowsMade)
        self.FreeThrowsAttempted = self.toThirtySix(FreeThrowsAttempted)
        self.FreeThrowsPercentage = self.toThirtySix(FreeThrowsPercentage)
        self.OffRebounds = self.toThirtySix(OffRebounds)
        self.DefRebounds = self.toThirtySix(DefRebounds)
        self.TotalRebounds = self.toThirtySix(OffRebounds) + self.toThirtySix(DefRebounds)
        self.Rebounds = self.toThirtySix(Rebounds)
        self.Assists = self.toThirtySix(Assists)
        self.Steals = self.toThirtySix(Steals)
        self.Blocks = self.toThirtySix(Blocks)
        self.Turnovers = self.toThirtySix(Turnovers)
        self.PersonalFouls = self.toThirtySix(PersonalFouls)
        self.Efficiency = Efficiency

    def toThirtySix(self, val48):
        if(val48 == None): return -1
        return (float(val48) * 36) / 48

    def printPlayer(self):
        print(
            self.Name, " ->",
            "Season ", self.Season, ":",
            "GamesPlayed ", self.GamesPlayed, ":",
            "MinutesPlayed ", self.MinutesPlayed, ":",
            "Points ", self.Points, ":",
            "FieldGoalsMade ", self.FieldGoalsMade, ":",
            "FieldGoalsAttempted ", self.FieldGoalsAttempted, ":",
            "FieldGoalPercentage ", self.FieldGoalPercentage, ":",
            "ThreeAttempted ", self.ThreeAttempted, ":",
            "ThreeMade ", self.ThreeMade, ":",
            "ThreePercentage ", self.ThreePercentage, ":",
            "FreeThrowsMade ", self.FreeThrowsMade, ":",
            "FreeThrowsAttempted ", self.FreeThrowsAttempted, ":",
            "FreeThrowsPercentage ", self.FreeThrowsPercentage, ":",
            "OffRebounds ", self.OffRebounds, ":",
            "DefRebounds ", self.DefRebounds, ":",
            "Rebounds ", self.Rebounds, ":",
            "Assists ", self.Assists, ":",
            "Steals ", self.Steals, ":",
            "Blocks ", self.Blocks, ":",
            "Turnovers ", self.Turnovers, ":",
            "PersonalFouls ", self.PersonalFouls, ":",
            "Efficiency ", self.Efficiency
        )
