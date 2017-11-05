
class Player:

    def __init__(self, Name, Season, ID, GamesPlayed=None, MinutesPlayed=None, Points=None,
                 FieldGoalsMade=None, FieldGoalsAttempted=None, FieldGoalPercentage=None,
                 ThreeMade=None, ThreeAttempted=None, ThreePercentage=None,
                 FreeThrowsMade=None, FreeThrowsAttempted=None, FreeThrowsPercentage=None,
                 OffRebounds=None, DefRebounds=None, Rebounds=None,
                 Assists=None, Steals=None, Block=None, Turnovers=None, Efficiency=None,PersonalFouls=None):
        self.Name = Name
        self.Season = Season
        self.psID = Season + ID
        self.ID = ID
        self.GamesPlayed = GamesPlayed
        self.MinutesPlayed = MinutesPlayed
        self.Points = Points
        self.FieldGoalsMade = FieldGoalsMade
        self.FieldGoalsAttempted = FieldGoalsAttempted
        self.FieldGoalPercentage = FieldGoalPercentage
        self.ThreeAttempted = ThreeAttempted
        self.ThreeMade = ThreeMade
        self.ThreePercentage = ThreePercentage
        self.FreeThrowsMade = FreeThrowsMade
        self.FreeThrowsAttempted = FreeThrowsAttempted
        self.FreeThrowsPercentage = FreeThrowsPercentage
        self.OffRebounds = OffRebounds
        self.DefRebounds = DefRebounds
        self.TotalRebounds = OffRebounds + DefRebounds
        self.Rebounds = Rebounds
        self.Assists = Assists
        self.Steals = Steals
        self.Block = Block
        self.Turnovers = Turnovers
        self.PersonalFouls = PersonalFouls
        self.Efficiency = Efficiency

    def toThirtySix(self, val48):
        return (val48 * 36) / 48

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
            "Block ", self.Block, ":",
            "Turnovers ", self.Turnovers, ":",
            "PersonalFouls ", self.PersonalFouls, ":",
            "Efficiency ", self.Efficiency
        )
