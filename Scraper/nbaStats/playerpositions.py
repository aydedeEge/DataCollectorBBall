import os
import time
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from load_config import read_config, set_env_vars
from pymysqlconnect import PyMySQLConn
from webpage import WebPage

BASE_URL_TEAM = "https://stats.nba.com/team/{team_id}/?Season={date}"

class PlayerPositions(WebPage):
    def __init__(self):
        config = {
            "host": os.environ["host"],
            "user": os.environ["user"],
            "pwd": os.environ["pwd"],
            "db": os.environ["db"],
        }
        self.sql = PyMySQLConn(config)
        super().__init__()

    def get_existing_players_from_db(self):
        connection = self.sql.connect_db()
        players = self.sql.select_all_players_command(connection)
        self.sql.close_connection(connection)

        return players

    def get_existing_teams_from_db(self):
        connection = self.sql.connect_db()
        teams = self.sql.select_all_teams_command(connection)
        self.sql.close_connection(connection)

        return teams

    def scrape_player_positions(self, team_id, date, threshold=5):
        player_positions = []

        self.load_page(
            BASE_URL_TEAM.format(
                team_id=team_id,
                date=date,
            )
        )
        
        html = self.get_page()
        soup = BeautifulSoup(html, "html.parser")

        all_player_rows = soup.tbody.find_all("tr")

        print("* Getting player positions for team " + str(team_id))

        attempt = 0
        try:
            for tr in all_player_rows:
                player_id_tag = tr.find_all("td")[0]
                player_position = self.get_embedded_text(tr.find_all("td")[2])
                player_id = player_id_tag.find("a")["href"].split("/")[2]

                player_positions.append(
                    {
                        "player_id": player_id,
                        "player_position": player_position
                    }
                )
        except TypeError as e:
            if attempt == threshold:
                raise e
            print("Page not loaded. Attempt: " +  str(attempt+1))
            time.sleep(1)
            attempt += 1
            

        return player_positions

    def get_player_positions_all_teams(self, date):
        player_positions_all_teams = []
        player_positions = []
        team_id_list = []
        teams = self.get_existing_teams_from_db()

        for team in teams:
            if team['teamid'] not in team_id_list:
                team_id_list.append(team['teamid'])

        for team_id in team_id_list:
            try:
                player_positions = self.scrape_player_positions(
                    team_id=team_id,
                    date=date
                )

                player_positions_all_teams = player_positions + player_positions_all_teams
            except Exception as e:
                raise e

        return player_positions_all_teams

    def get_embedded_text(self, tag):
        for child in tag.descendants:
            if child.string is not None:
                return child.string

    def generate_dates(self, start_date=1979, end_date=2018):
        dates = []
        all_player_ids = {}
        first_date = start_date
        second_date = first_date+1

        while (first_date<end_date):
            dates.append('{first_date}-{first_digit}{second_digit}'.format(first_date=first_date, first_digit=str(second_date)[2], second_digit=str(second_date)[3]))
            first_date+=1
            second_date+=1

        return dates

data = read_config()
set_env_vars(data)
pp = PlayerPositions()
print(pp.get_player_positions_all_teams("2016-17"))