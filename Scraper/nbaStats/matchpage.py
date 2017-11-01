import os
import time
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from load_config import read_config, set_env_vars
from pymysqlconnect import PyMySQLConn
from webpage import WebPage

BASE_TEAM_ID_URL = "https://stats.nba.com/teams/traditional/?sort=W_PCT&dir=-1&Season={date}&SeasonType={season_type}"
BASE_MATCH_URL = "https://stats.nba.com/team/{team_id}/boxscores/?Season={date}&SeasonType={season_type}"

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

    # Add start_date and end_date args
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

class MatchPage(WebPage):
    def __init__(self):
        super().__init__()

    def get_matches(self, team_id, date, season_type, all_matches=[], threshold=200):
        matches_list = []
        self.load_page(
            BASE_MATCH_URL.format(
                team_id=team_id,
                date=date,
                season_type=season_type,
            )
        )

        self.dom_change_event_class(
            tag_attribute="class",
            tag_attribute_value="stats-table-pagination__select",
            new_value="string:All",
            time_out=6,
        )

        html = self.get_page()
        soup = BeautifulSoup(html, "html.parser")

        try:
            all_match_rows = soup.tbody.find_all("tr")
        except AttributeError as e:
            matches_list.append(
                Match(
                    hteam="",
                    ateam="",
                    date="0-0-0",
                    winner="NA",
                )
            )
            return matches_list

        try:
            for tr in all_match_rows:
                stat_row = tr.find_all("td")
                match_up = self.get_embedded_text(stat_row[0])
                mdate = self.transform_date(match_up.split(" - ")[0])
                winloss = self.get_embedded_text(stat_row[1])
                hteam, ateam, winner = self.get_teams_and_winner(match_up.split(" - ")[1], winloss)

                match = Match(
                    hteam=hteam,
                    ateam=ateam,
                    date=mdate,
                    winner=winner
                )

                matches_list.append(match)
        except Exception as e:
            raise e
        print("* {length} matches gathered for team {tid}".format(length=len(matches_list),tid=team_id))
        if len(matches_list) < threshold:
            for match in matches_list:
                if match not in all_matches:
                    all_matches.append(match)
        print("*** {length} matches in all_matches".format(length=len(all_matches)))
        return matches_list

    #Pretty hard-coded
    def get_embedded_text(self, tag):
        for child in tag.descendants:
            if child.string is not None:
                return child.string

    def get_teams_and_winner(self, text, win_loss):
        if 'vs.' in text:
            home = text.split('vs.')[0].replace(" ", "")
            away = text.split('vs.')[1].replace(" ", "")

            if win_loss == "W":
                winner = home
            else:
                winner = away
        elif '@' in text:
            away = text.split('@')[0].replace(" ", "")
            home = text.split('@')[1].replace(" ", "")

            if win_loss == "W":
                winner = away
            else:
                winner = home
            
        return home, away, winner

    # Mar 08, 2017 unformatted
    def transform_date(self, date):
        months = {
            "jan": '01',
            "feb": '02',
            "mar": '03',
            "apr": '04',
            "may": '05',
            "jun": '06',
            "jul": '07',
            "aug": '08',
            "sep": '09',
            "oct": '10',
            "nov": '11',
            "dec": '12',
        }

        first, second, third = date.split(" ")[0], date.split(" ")[1], date.split(" ")[2]
        day = second.replace(",", "")
        month = months[first.lower()]
        year = third
        formatted_date = '{year}-{month}-{day}'.format(year=year, month=month, day=day)
        
        return formatted_date

    def get_matches_all_teams(self, date, season_type, all_teams):
        all_matches = []

        try:
            for name, tid in all_teams.items():
                self.get_matches(
                    team_id=tid,
                    date=date,
                    season_type=season_type,
                    all_matches=all_matches,
                )
        except Exception as e:
            pass

        return all_matches

    def get_matches_all_dates(self, season_type, start_date=1979, end_date=2018, db=False):
        
        tp = TeamPage()
        dates = []
        all_date_matches = {}
        first_date = start_date
        second_date = first_date+1

        while (first_date<end_date):
            dates.append('{first_date}-{first_digit}{second_digit}'.format(first_date=first_date, first_digit=str(second_date)[2], second_digit=str(second_date)[3]))
            first_date+=1
            second_date+=1

        for date in dates:
            teams = tp.get_all_team_ids(
                date=date,
                season_type=season_type,
            )
            print("** Gathering matches for {date}".format(date=date))
            matches = self.get_matches_all_teams(
                date=date,
                season_type="Regular%20Season",
                all_teams=teams,
            )

            if db:
                print("** Pushing matches from {date} to db".format(date=date))
                self.push_matches_to_db(matches)
                continue

            all_date_matches[date] = matches

            print("** {date} matches gathered".format(date=date))
        
        return all_date_matches

    def push_matches_to_db(self, matches):
        config = {
            "host": os.environ["host"],
            "user": os.environ["user"],
            "pwd": os.environ["pwd"],
            "db": os.environ["db"],
        }

        sql = PyMySQLConn(config)
        connection = sql.connect_db()

        length = len(matches)
        iterator = 1

        for match in matches:
            hteam = match.get_hteam()
            ateam = match.get_ateam()
            winner = match.get_winner()
            date = match.get_date()

            sql.insert_match(
                connection=connection,
                hteam=hteam,
                ateam=ateam,
                winner=winner,
                date=date,
            )
            print("+ {iterator}/{length} - Pushed match to db".format(iterator=iterator, length=length))
            iterator+=1
        sql.close_connection(connection)

