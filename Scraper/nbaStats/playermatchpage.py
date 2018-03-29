import os
import time
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from load_config import read_config, set_env_vars
from pymysqlconnect import PyMySQLConn
from webpage import WebPage
from allplayerpage import AllPlayerPage

BASE_PLAYER_URL = "https://stats.nba.com/player/{player_id}/{stat_type}/?Season={date}&SeasonType={season_type}"
BASE_PLAYER_URL_N_GAMES = "https://stats.nba.com/player/{player_id}/{stat_type}/?Season={date}&SeasonType={season_type}&LastNGames={n_games}"
BASE_PLAYER_URL_FROM_TO = "https://stats.nba.com/player/{player_id}/{stat_type}/?Season={date}&SeasonType={season_type}&DateFrom={date_from}&DateTo={date_to}&sort=gdate&dir=1"
DATE_FORMAT = "03%2F14%2F2018"

class PlayerPage(WebPage):
    def __init__(self):
        super().__init__()

    def get_player_matches(self, player_id, date, stat_type, season_type, n_games=None, to=4, date_from=None, date_to=None):
        matches_list = []
        if n_games is not None:
            self.load_page(
                BASE_PLAYER_URL_N_GAMES.format(
                    player_id=player_id,
                    date=date,
                    season_type=season_type,
                    stat_type=stat_type,
                    n_games=n_games
                )
            )

        elif date_from is not None and date_to is not None:
            self.load_page(
                BASE_PLAYER_URL_FROM_TO.format(
                    player_id=player_id,
                    date=date,
                    season_type=season_type,
                    stat_type=stat_type,
                    date_from=date_from,
                    date_to=date_to
                )
            )

        else:
            self.load_page(
                BASE_PLAYER_URL.format(
                    player_id=player_id,
                    date=date,
                    season_type=season_type,
                    stat_type=stat_type
                )
            )

            # time.sleep(3)
            self.dom_change_event_class(
                tag_attribute="class",
                tag_attribute_value="stats-table-pagination__select",
                new_value="string:All",
            )

        time_out = to
        a = 0

        while a < time_out+1:
            try:
                html = self.get_page()
                soup = BeautifulSoup(html, "html.parser")
                all_match_rows = soup.tbody.find_all("tr")
                break
            except AttributeError as e:
                if a < time_out:
                    print(e)
                    print("Page loading attempt {a}/{time_out}".format(a=a+1, time_out=time_out))
                    a += 1
                    time.sleep(1)
                else:
                    print("Here")
                    matches_list.append(
                        {
                            "pid": player_id,
                            "winloss": "Null",
                            "minutes": 0,
                            "points": 0,
                            "FGM": 0,
                            "FGA": 0,
                            "FG%": 0,
                            "3PM": 0,
                            "3PA": 0,
                            "3P%": 0,
                            "FTM": 0,
                            "FTA": 0,
                            "FT%": 0,
                            "ORB": 0,
                            "DRB": 0,
                            "REB": 0,
                            "AST": 0,
                            "STL": 0,
                            "BLK": 0,
                            "TOV": 0,
                            "PF": 0,
                            "plusminus": 0,
                            "mdate": "0-1-1",
                            "pteam": "NA",
                            "oteam": "NA",
                            "home_away": "NA"
                        }
                    )
                    return matches_list
        
        # Should probably remove this try catch
        try:
            for tr in all_match_rows:
                stat_row = tr.find_all("td")
                match_up = self.get_embedded_text(stat_row[0])
                mdate = self.transform_date(match_up.split(" - ")[0])
                pteam, oteam, home_away = self.get_teams_from_text(match_up.split(" - ")[1])
                win_loss = self.get_embedded_text(stat_row[1])
                mins_played = self.get_embedded_text(stat_row[2])
                pts = self.get_embedded_text(stat_row[3])
                fgm = self.get_embedded_text(stat_row[4])
                fga = self.get_embedded_text(stat_row[5])
                fg_percent = self.get_embedded_text(stat_row[6])
                three_pm = self.get_embedded_text(stat_row[7])
                three_pa = self.get_embedded_text(stat_row[8])
                three_percent = self.get_embedded_text(stat_row[9])
                ftm = self.get_embedded_text(stat_row[10])
                fta = self.get_embedded_text(stat_row[11])
                ft_percent = self.get_embedded_text(stat_row[12])
                oreb = self.get_embedded_text(stat_row[13])
                dreb = self.get_embedded_text(stat_row[14])
                reb = self.get_embedded_text(stat_row[15])
                ast = self.get_embedded_text(stat_row[16])
                stl = self.get_embedded_text(stat_row[17])
                blk = self.get_embedded_text(stat_row[18])
                tov = self.get_embedded_text(stat_row[19])
                pf = self.get_embedded_text(stat_row[20])
                plus_minus = self.get_embedded_text(stat_row[21])

                matches_list.append(
                    {
                        "pid": player_id,
                        "winloss": win_loss,
                        "minutes": mins_played,
                        "points": pts,
                        "FGM": fgm,
                        "FGA": fga,
                        "FG%": fg_percent,
                        "3PM": three_pm,
                        "3PA": three_pa,
                        "3P%": three_percent,
                        "FTM": ftm,
                        "FTA": fta,
                        "FT%": ft_percent,
                        "ORB": oreb,
                        "DRB": dreb,
                        "REB": reb,
                        "AST": ast,
                        "STL": stl,
                        "BLK": blk,
                        "TOV": tov,
                        "PF": pf,
                        "plusminus": plus_minus,
                        "mdate": mdate,
                        "pteam": pteam,
                        "oteam": oteam,
                        "home_away": home_away
                    }
                )
        except Exception as e:
            raise e
        return matches_list

    
    def push_player_matches_to_db(self, matches):
        config = {
            "host": os.environ["host"],
            "user": os.environ["user"],
            "pwd": os.environ["pwd"],
            "db": os.environ["db"],
        }
        sql = PyMySQLConn(config)
        connection = sql.connect_db()
        sql.insert_player_matches(connection=connection, matches=matches)
        sql.close_connection(connection=connection)
    
    def push_all_pmatches_to_db_by_date(self, date, season_type, stat_type, players, n_games=None, date_from=None, date_to=None):
        length = len(players)
        iterator = 1

        if n_games is not None:
            for key, value in players.items():
                print("* {iterator}/{length} - Gathering player matches for {key}...".format(iterator=iterator, length=length, key=key))
                pmatches = self.get_player_matches(
                    player_id=value,
                    date=date,
                    season_type=season_type,
                    stat_type=stat_type,
                    n_games=n_games
                )
                print('+ {iterator}/{length} - Pushing records for {key} to db...'.format(iterator=iterator, length=length, key=key))
                self.push_player_matches_to_db(pmatches)
                iterator+=1

        elif date_from is not None and date_to is not None:
            for key, value in players.items():
                print("* {iterator}/{length} - Gathering player matches for {key}...".format(iterator=iterator, length=length, key=key))
                pmatches = self.get_player_matches(
                    player_id=value,
                    date=date,
                    season_type=season_type,
                    stat_type=stat_type,
                    date_from=date_from,
                    date_to=date_to
                )
                print('+ {iterator}/{length} - Pushing records for {key} to db...'.format(iterator=iterator, length=length, key=key))
                self.push_player_matches_to_db(pmatches)
                iterator+=1

        else:
            for key, value in players.items():
                print("* {iterator}/{length} - Gathering player matches for {key}...".format(iterator=iterator, length=length, key=key))
                pmatches = self.get_player_matches(
                    player_id=value,
                    date=date,
                    season_type=season_type,
                    stat_type=stat_type
                )
                print('+ {iterator}/{length} - Pushing records for {key} to db...'.format(iterator=iterator, length=length, key=key))
                self.push_player_matches_to_db(pmatches)
                iterator+=1


    #Pretty hard-coded
    def get_embedded_text(self, tag):
        for child in tag.descendants:
            if child.string is not None:
                return child.string


    def get_teams_from_text(self, text):
        if 'vs.' in text:
            team1 = text.split('vs.')[0].replace(" ", "")
            team2 = text.split('vs.')[1].replace(" ", "")
            home_away = "H"
        elif '@' in text:
            team1 = text.split('@')[0].replace(" ", "")
            team2 = text.split('@')[1].replace(" ", "")
            home_away = "A"

        return team1, team2, home_away


    # Mar 08, 2017 unformatted
    def transform_date(self, date):
        months = {
            "Jan": '01',
            "Feb": '02',
            "Mar": '03',
            "Apr": '04',
            "May": '05',
            "Jun": '06',
            "Jul": '07',
            "Aug": '08',
            "Sep": '09',
            "Oct": '10',
            "Nov": '11',
            "Dec": '12',
        }

        first, second, third = date.split(" ")[0], date.split(" ")[1], date.split(" ")[2]
        day = second.replace(",", "")
        month = months[first]
        year = third
        formatted_date = '{year}-{month}-{day}'.format(year=year, month=month, day=day)
        
        return formatted_date
