
class Player:

    def __init__(self, Name, Season, ID, Wins=-1, Losses=-1, Age=-1, Team=-1, GamesPlayed=-1, MinutesPlayed=-1, Points=-1,
                 FieldGoalsMade=-1, FieldGoalsAttempted=-1, FieldGoalPercentage=-1,
                 ThreeMade=-1, ThreeAttempted=-1, ThreePercentage=-1,
                 FreeThrowsMade=-1, FreeThrowsAttempted=-1, FreeThrowPercentage=-1,
                 OffRebounds=-1, DefRebounds=-1, Rebounds=-1,
                 Assists=-1, Steals=-1, Blocks=-1, Turnovers=-1,PersonalFouls=-1, PlusMinus=-1):
        self.Name = Name
        self.Season = Season
        self.Age = Age
        self.Team = Team
        self.Wins = Wins
        self.Losses = Losses
        self.psID = Season + ID
        self.ID = ID
        self.GamesPlayed = float(GamesPlayed)
        self.MinutesPlayed = float(MinutesPlayed)
        self.Points = float(Points)
        self.FieldGoalsMade = float(FieldGoalsMade)
        self.FieldGoalsAttempted = float(FieldGoalsAttempted)
        self.FieldGoalPercentage = float(FieldGoalPercentage)
        self.ThreeAttempted = float(ThreeAttempted)
        self.ThreeMade = float(ThreeMade)
        self.FreeThrowsMade = float(FreeThrowsMade)
        self.ThreePercentage = float(ThreePercentage)
        self.FreeThrowPercentage = float(FreeThrowPercentage)
        self.FreeThrowsAttempted = float(FreeThrowsAttempted)
        self.OffRebounds = float(OffRebounds)
        self.DefRebounds = float(DefRebounds)
        self.TotalRebounds = float(OffRebounds) + float(DefRebounds)
        self.Rebounds = float(Rebounds)
        self.Assists = float(Assists)
        self.Steals = float(Steals)
        self.Blocks = float(Blocks)
        self.Turnovers = float(Turnovers)
        self.PersonalFouls = float(PersonalFouls)
        self.PlusMinus = float(PlusMinus)
        self.Score = self.calculateScore()
    
    def calculateScore(self):
        FG_3_SCORE = 3
        FG_SCORE = 2
        FT_SCORE = 1
        RB_SCORE = 1.2
        AST_SCORE = 1.5
        BLK_SCORE = 3
        STEAL_SCORE = 3
        TURNOVER_SCORE = -1
        SEASON = 2017
        return  self.FieldGoalsMade * FG_SCORE + self.ThreeMade * FG_3_SCORE + self.FreeThrowsMade * FT_SCORE +\
                 self.TotalRebounds * RB_SCORE + self.Assists * AST_SCORE + self.Blocks * BLK_SCORE +\
                 self.Steals * STEAL_SCORE + self.Turnovers * TURNOVER_SCORE

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
            "FreeThrowPercentage ", self.FreeThrowPercentage, ":",
            "OffRebounds ", self.OffRebounds, ":",
            "DefRebounds ", self.DefRebounds, ":",
            "Rebounds ", self.Rebounds, ":",
            "Assists ", self.Assists, ":",
            "Steals ", self.Steals, ":",
            "Blocks ", self.Blocks, ":",
            "Turnovers ", self.Turnovers, ":",
            "PersonalFouls ", self.PersonalFouls, ":"
        )
