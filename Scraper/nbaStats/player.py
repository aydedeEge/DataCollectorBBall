
class Player:

    def __init__(self, Season, Name, ID, GamesPlayed=None, MinutesPlayed=None, Points=None,
                 FieldGoalsMade=None, FieldGoalsAttempted=None, FieldGoalPercentage=None,
                 ThreeMade=None, ThreeAttempted=None, ThreePercentage=None,
                 FreeThrowsMade=None, FreeThrowsAttempted=None, FreeThrowsPercentage=None,
                 OffRebounds=None, DefRebounds=None, Rebounds=None,
                 Assists=None, Steals=None, Block=None, Turnovers=None, PersonalFouls=None, Efficiency=None):
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

    def printPlayer(self):
        print(
            self.Name, " ->",
            self.Season, ":",
            self.GamesPlayed, ":",
            self.MinutesPlayed, ":",
            self.Points, ":",
            self.FieldGoalsMade, ":",
            self.FieldGoalsAttempted, ":",
            self.FieldGoalPercentage, ":",
            self.ThreeAttempted, ":",
            self.ThreeMade, ":",
            self.ThreePercentage, ":",
            self.FreeThrowsMade, ":",
            self.FreeThrowsAttempted, ":",
            self.FreeThrowsPercentage, ":",
            self.OffRebounds, ":",
            self.DefRebounds, ":",
            self.Rebounds, ":",
            self.Assists, ":",
            self.Steals, ":",
            self.Block, ":",
            self.Turnovers, ":",
            self.Efficiency
        )
