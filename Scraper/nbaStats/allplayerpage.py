import os
import time
import sys
import MySQLdb

from bs4 import BeautifulSoup
from selenium import webdriver
from load_config import read_config, set_env_vars
from pymysqlconnect import PyMySQLConn
from webpage import WebPage
from player import Player

BASE_PLAYER_URL = "https://stats.nba.com/player/{player_id}/{stat_type}/?Season={date}&SeasonType={season_type}"
BASE_ALL_PLAYER_URL = "https://stats.nba.com/players/traditional/?sort=PTS&dir=-1&Season={date}&SeasonType={season_type}"


class AllPlayerPage(WebPage):
    def __init__(self):
        super().__init__()

    # season_type possible values:
    #   Regular Season: "Regular%20Season"
    #   Playoffs: "Playoffs"
    #   Preseason: "Pre%20Season"
    # date format:
    #   2016 and 2017: "2016-17"

    def get_all_player_ids(self, date, season_type, all_date_player_ids={}):
        all_player_ids_dict = {}

        self.load_page(BASE_ALL_PLAYER_URL.format(
            date=date, season_type=season_type))
        # time.sleep(3)
        print('* Gathering player ids for {date}'.format(date=date))

        self.dom_change_event_class(
            tag_attribute="class",
            tag_attribute_value="stats-table-pagination__select",
            new_value="string:All",
        )
        html = self.get_page()
        soup = BeautifulSoup(html, "html.parser")

        all_player_rows = soup.tbody.find_all("tr")

        for tr in all_player_rows:
            player_id_tag = tr.find_all("td")[1]
            player_name = player_id_tag.find("a").string
            player_id = player_id_tag.find("a")["href"].split("/")[2]
            try:
                all_player_ids_dict[player_name] = player_id
                if player_name not in all_date_player_ids:
                    all_date_player_ids[player_name] = player_id
            except Exception as e:
                pass

        return all_player_ids_dict

    def get_embedded_text(self, tag):
        for child in tag.descendants:
            if child.string is not None:
                return child.string

    def get_all_player_stats(self, date, season_type, all_date_player_stats=[]):

        self.load_page(BASE_ALL_PLAYER_URL.format(
            date=date, season_type=season_type) + "&PerMode=Per36")

        print('* Gathering player ids for {date}'.format(date=date))

        self.dom_change_event_class(
            tag_attribute="class",
            tag_attribute_value="stats-table-pagination__select",
            new_value="string:All",
        )
        html = self.get_page()
        soup = BeautifulSoup(html, "html.parser")

        all_player_rows = soup.tbody.find_all("tr")
        SEASON = date[:4]
        print(SEASON)
        for tr in all_player_rows:
            stat_row = tr.find_all("td")

            player_id_tag = stat_row[1]
            player_name = player_id_tag.find("a").string
            player_id = player_id_tag.find("a")["href"].split("/")[2]
            TEAM = self.get_embedded_text(stat_row[2])
            AGE = self.get_embedded_text(stat_row[3])
            GP = self.get_embedded_text(stat_row[4])
            WINS = self.get_embedded_text(stat_row[5])
            LOSSES = self.get_embedded_text(stat_row[6])
            TOTAL_MINUTES = self.get_embedded_text(stat_row[7])
            PTS = self.get_embedded_text(stat_row[8])
            FGM = self.get_embedded_text(stat_row[9])
            FGA = self.get_embedded_text(stat_row[10])
            FGperc = self.get_embedded_text(stat_row[11])
            ThreePM = self.get_embedded_text(stat_row[12])
            ThreePA = self.get_embedded_text(stat_row[13])
            ThreePerc = self.get_embedded_text(stat_row[14])
            FTM = self.get_embedded_text(stat_row[15])
            FTA = self.get_embedded_text(stat_row[16])
            FTperc = self.get_embedded_text(stat_row[17])
            OREB = self.get_embedded_text(stat_row[18])
            DREB = self.get_embedded_text(stat_row[19])
            REB = self.get_embedded_text(stat_row[20])
            AST = self.get_embedded_text(stat_row[21])
            TOV = self.get_embedded_text(stat_row[22])
            STL = self.get_embedded_text(stat_row[23])
            BLK = self.get_embedded_text(stat_row[24])
            PF = self.get_embedded_text(stat_row[25])
            PM = self.get_embedded_text(stat_row[29])

            player = Player(Name=player_name,Season=SEASON, Team=TEAM, Age=AGE, Wins=WINS, Losses=LOSSES,
                ID=player_id,GamesPlayed=GP,MinutesPlayed=TOTAL_MINUTES,
                Points=PTS,FieldGoalsMade=FGM,FieldGoalsAttempted=FGA,FieldGoalPercentage=FGperc, 
                ThreeMade=ThreePM, ThreeAttempted=ThreePA,ThreePercentage=ThreePerc,FreeThrowsMade=FTM,
                FreeThrowsAttempted=FTA, FreeThrowPercentage=FTperc,OffRebounds=OREB,DefRebounds=DREB,
                Rebounds=REB,Assists=AST,Steals=STL,Blocks=BLK,Turnovers=TOV, PersonalFouls=PF, PlusMinus = PM)
            try:
                if player_id not in all_date_player_stats:
                    all_date_player_stats.append(player)

            except Exception as e:
                pass
        return all_date_player_stats

    def get_all_playerStats_all_date(self, season_type):
        dates = []
        all_player_stats = []
        first_date = 1996
        second_date = first_date + 1

        while (first_date < 2018):
            dates.append('{first_date}-{first_digit}{second_digit}'.format(first_date=first_date,
                                                                           first_digit=str(second_date)[2], second_digit=str(second_date)[3]))
            first_date += 1
            second_date += 1

        for date in dates:
            self.get_all_player_stats(
                date=date,
                season_type=season_type,
                all_date_player_stats=all_player_stats
            )
        return all_player_stats

    def get_all_player_ids_all_dates(self, season_type):
        dates = []
        all_player_ids = {}
        first_date = 1979
        second_date = first_date + 1

        while (first_date < 2018):
            dates.append('{first_date}-{first_digit}{second_digit}'.format(first_date=first_date,
                                                                           first_digit=str(second_date)[2], second_digit=str(second_date)[3]))
            first_date += 1
            second_date += 1

        for date in dates:
            self.get_all_player_ids(
                date=date,
                season_type=season_type,
                all_date_player_ids=all_player_ids
            )

        return all_player_ids
        # Pretty hard-coded

    def get_embedded_text(self, tag):
        for child in tag.descendants:
            if child.string is not None:
                return child.string

    def push_all_player_stats_to_db(self, playerStats):
        connection = MySQLdb.connect(
            host=os.environ["host"],    # your host, usually localhost
            user=os.environ["user"],         # your username
            passwd=os.environ["pwd"],  # your password
            db=os.environ["db"]
        )
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        for player in playerStats:
            if(player.Name != None):
                command = "INSERT INTO `d2matchb_bball`.`player_stats` (`player_id`, `player_stats_id`," +\
                    "`name`, `season`, `team`, `age`, `FG_36`, `FGA_36`, `3P_36`, `3PA_36`, `FT_36`," +\
                    "`FTA_36`, `ORB_36`, `TRB_36`, `AST_36`, `STL_36`, `BLK_36`, `TOV_36`, `PF_36`," +\
                    "`PTS_36`, `FG%`, `3P%`, `FT%`, `score`, `W`, `L`, `Total_Minutes`, `PM_36`) VALUES (" + str(player.ID) + "," + str(player.psID) +\
                    ",\"" + str(player.Name) + "\"," + str(player.Season) + ",'" + str(player.Team) +\
                    "'," + str(player.Age) + "," + str(player.FieldGoalsMade) + "," + str(player.FieldGoalsAttempted) + "," + str(player.ThreeMade) + "," + str(player.ThreeAttempted) +\
                    "," + str(player.FreeThrowsMade) + "," + str(player.FreeThrowsAttempted) + "," + str(player.OffRebounds) +\
                    "," + str(player.TotalRebounds) + "," + str(player.Assists) + "," + str(player.Steals) + "," + str(player.Blocks) +\
                    "," + str(player.Turnovers) + "," + str(player.PersonalFouls) + "," + str(player.Points) +\
                    "," + str(player.FieldGoalPercentage) + "," + str(player.ThreePercentage) + "," + str(player.FreeThrowPercentage) +\
                    "," + str(player.Score) + "," + str(player.Wins) + "," + str(player.Losses) + "," + str(player.MinutesPlayed) +\
                    "," + str(player.PlusMinus) + ");"
                print(command)
                cursor.execute(command)
        connection.commit()
        connection.close()

    def push_all_player_ids_to_db(self, players):
        config = {
            "host": os.environ["host"],
            "user": os.environ["user"],
            "pwd": os.environ["pwd"],
            "db": os.environ["db"],
        }
        sql = PyMySQLConn(config)
        connection = sql.connect_db()
        pid = ""
        f_name = ""
        l_name = ""
        length = len(players)
        iterator = 1

        for k, v in players.items():
            pid = v
            f_name = self.single_quote_name(k.split(" ")[0])
            # Some players don't have first names
            try:
                l_name = self.single_quote_name(k.split(" ")[1])
            except IndexError as e:
                l_name = ""
            sql.insert_players_command(
                connection=connection, pid=pid, f_name=f_name, l_name=l_name)
            print("+ {iterator}/{length} - Pushed player: {f_name} {l_name} to db.".format(
                iterator=iterator, length=length, f_name=f_name, l_name=l_name))
            iterator += 1
        sql.close_connection(connection)

    def single_quote_name(self, name):
        sname = ""
        if "'" in name:
            sname = name.split("'")[0] + "''" + name.split("'")[1]
            return sname
        sname = name
        return sname
