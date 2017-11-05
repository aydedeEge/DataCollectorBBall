class Match():
    def __init__(self, hteam, ateam, date, winner):
        self.hteam = hteam
        self.ateam = ateam
        self.date = date
        self.winner = winner

    def __str__(self):
        string = "Home: {hteam}, Away: {ateam}, Date: {date}, Winner: {winner}".format(
            hteam=self.hteam,
            ateam=self.ateam,
            date=self.date,
            winner=self.winner
        )
        return string

    def __eq__(self, other):
        return self.hteam == other.hteam and self.ateam == other.ateam and self.date == other.date

    def get_hteam(self):
        return self.hteam

    def get_ateam(self):
        return self.ateam

    def get_date(self):
        return self.date

    def get_winner(self):
        return self.winner