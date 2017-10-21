import os
import pymysql
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from load_config import read_config, set_env_vars

SQL_INSERT_COMMAND_BASE = "INSERT INTO `players` (`pid`, `first_name`, `last_name`) VALUES ('{pid}', '{f_name}', '{l_name}');"
SQL_SELECT_COMMAND_BASE = "SELECT * FROM `{table}` LIMIT 5"

BASE_PLAYER_URL = "https://stats.nba.com/player/{player_id}/{stat_type}/?Season={date}&SeasonType={season_type}"
BASE_ALL_PLAYER_URL = "https://stats.nba.com/leaders/?Season={date}&SeasonType={season_type}"
TEST_ALL_PLAYER_URL = "https://stats.nba.com/leaders/?Season=2016-17&SeasonType=Regular%20Season"

class PyMySQLConn:
    def __init__(self, config):
        self.host = config.get("host")
        self.user = config.get("user")
        self.pwd = config.get("pwd")
        self.db = config.get("db")

    def reset_config(self, config):
        pass

    def connect_db(self):
        connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.pwd,
            db=self.db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        return connection

    def execute_command(self, connection, command):
        try:
            with connection.cursor() as cursor:
                cursor.execute(command)
            connection.commit()
        except Exception as e:
            raise e

    def insert_players_command(self, connection, pid, f_name, l_name):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    SQL_INSERT_COMMAND_BASE.format(
                        pid=pid,
                        f_name=f_name,
                        l_name=l_name
                    )
                )
            connection.commit()
        except Exception as e:
            raise e
    
    def select_from_table_command(self, connection, table):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    SQL_SELECT_COMMAND_BASE.format(
                        table=table
                    )
                )
        except Exception as e:
            raise e

    def commit_changes(self, connection):
        connection.commit()

    def close_connection(self, connection):
        connection.close()


class WebPage:

    tag_attribute_dict = {
        "id": "getElementById",
        "class": "getElementsByClassName",
    }

    def __init__(self):
        self.driver = webdriver.Chrome(f'{os.getcwd()}/chromedriver')

    def load_page(self, url):
        self.url = url
        self.driver.get(self.url)
    
    def get_page(self):
        return self.driver.page_source

    # Must call load_page at least once before
    def dom_change_event_class(self, tag_attribute, tag_attribute_value, new_value):
        tag_attr_command = "getElementsByClassName"

        try:
            # Need to change the first line of execute_script; [0] hard coded
            self.driver.execute_script(f'''
                var el = document.{tag_attr_command}("{tag_attribute_value}")[0];
                el.value = "{new_value}";
                var event = document.createEvent("HTMLEvents");
                event.initEvent("change", true, false);
                el.dispatchEvent(event);
            ''')
        except Exception as e:
            raise e

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

        self.load_page(BASE_ALL_PLAYER_URL.format(date=date, season_type=season_type))
        time.sleep(2)
        print(f'Gathering player ids for {date}')

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


    def get_all_player_ids_all_dates(self, season_type):
        dates = []
        all_player_ids = {}
        first_date = 1979
        second_date = first_date+1

        while (first_date<2018):
            dates.append(f'{first_date}-{str(second_date)[2]}{str(second_date)[3]}')
            first_date+=1
            second_date+=1
        
        for date in dates:
            self.get_all_player_ids(
                date=date,
                season_type=season_type,
                all_date_player_ids=all_player_ids
            )
        
        return all_player_ids

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

        for k,v in players.items():
            pid = v
            f_name = single_quote_name(k.split(" ")[0])
            # Some players don't have first names
            try:
                l_name = single_quote_name(k.split(" ")[1])
            except IndexError as e:
                l_name = ""
            sql.insert_players_command(connection=connection, pid=pid, f_name=f_name, l_name=l_name)
        sql.close_connection(connection)


class PlayerPage(WebPage):
    def __init__(self):
        super().__init__()

    def get_player_matchs(self, player_id, date, stat_type, season_type):
        matches_dict = {}
        self.load_page(
            BASE_PLAYER_URL.format(
                player_id=player_id,
                date=date,
                season_type=season_type,
                stat_type=stat_type
            )
        )
        self.dom_change_event_class(
            tag_attribute="class",
            tag_attribute_value="stats-table-pagination__select",
            new_value="string:All",
        )
        html = self.get_page()
        soup = BeautifulSoup(html, "html.parser")

        all_match_rows = soup.tbody.find_all("tr")
        for tr in all_match_rows:
            stat_row = tr.find_all("td")
            match_up = self.get_embedded_text(stat_row[0])
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

            matches_dict[match_up] = {
                "match_up": match_up,
                "win_loss": win_loss,
                "mins_played": mins_played,
                "pts": pts,
                "fgm": fgm,
                "fga": fga,
                "fg_percent": fg_percent,
                "three_pm": three_pm,
                "three_pa": three_pa,
                "three_percent": three_percent,
                "ftm": ftm,
                "fta": fta,
                "ft_percent": ft_percent,
                "oreb": oreb,
                "dreb": dreb,
                "reb": reb,
                "ast": ast,
                "stl": stl,
                "blk": blk,
                "tov": tov,
                "pf": pf,
                "plus_minus": plus_minus,
            }

        print(matches_dict)
        return matches_dict


    #Pretty hard-coded
    def get_embedded_text(self, tag):
        for child in tag.descendants:
            if child.string is not None:
                return child.string

    
def single_quote_name(name):
    sname = ""
    if "'" in name:
        sname = name.split("'")[0] + "''" + name.split("'")[1]
        return sname
    sname = name
    return sname


def main():
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)

    wp = AllPlayerPage()
    players = wp.get_all_player_ids(
        date="2016-2017",
        season_type="Regular%20Season",
    )
    wp.push_all_player_ids_to_db(players)
    

main()
