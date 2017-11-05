import os
import time
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from load_config import read_config, set_env_vars
from pymysqlconnect import PyMySQLConn
from webpage import WebPage

BASE_TEAM_ID_URL = "https://stats.nba.com/teams/traditional/?sort=W_PCT&dir=-1&Season={date}&SeasonType={season_type}"

class TeamPage(WebPage):
    def __init__(self):
        super().__init__()

    def get_all_team_ids(self, date, season_type, all_date_team_ids={}):
        all_team_ids_dict = {}

        self.load_page(BASE_TEAM_ID_URL.format(date=date, season_type=season_type))
        print("* Gathering team ids for {date}".format(date=date))

        self.dom_change_event_class(
            tag_attribute="class",
            tag_attribute_value="stats-table-pagination__select",
            new_value="string:All",
            time_out=5,
        )
        html = self.get_page()
        soup = BeautifulSoup(html, "html.parser")

        all_team_rows = soup.tbody.find_all("tr")

        for tr in all_team_rows:
            team_id_tag = tr.find_all("td")[1]
            team_name = team_id_tag.find("a").string
            team_id = team_id_tag.find("a")["href"].split("/")[2]
            try:
                all_team_ids_dict[team_name] = team_id

                if team_name not in all_date_team_ids:
                    all_date_team_ids[team_name] = team_id
            except Exception as e:
                pass
 
        return all_team_ids_dict


    def get_all_team_ids_all_dates(self, season_type, start_date=1996, end_date=2018):
        dates = []
        all_team_ids = {}
        first_date = start_date
        second_date = first_date+1

        while (first_date<end_date):
            dates.append('{first_date}-{first_digit}{second_digit}'.format(first_date=first_date, first_digit=str(second_date)[2], second_digit=str(second_date)[3]))
            first_date+=1
            second_date+=1

        for date in dates:
            self.get_all_team_ids(
                date=date,
                season_type=season_type,
                all_date_team_ids=all_team_ids
            )

        return all_team_ids

    def push_teams_to_db(self, teams):
        config = {
            "host": os.environ["host"],
            "user": os.environ["user"],
            "pwd": os.environ["pwd"],
            "db": os.environ["db"],
        }

        sql = PyMySQLConn(config)
        connection = sql.connect_db()

        length = len(teams)
        iterator = 1

        for name, teamid in teams.items():
            sql.insert_team(
                connection=connection,
                teamid=teamid,
                name=name,
            )
            print("+ {iterator}/{length} - Pushed {name} to db".format(iterator=iterator, length=length, name=name))
            iterator+=1