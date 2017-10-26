import os
import pymysql
import time
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from load_config import read_config, set_env_vars

SQL_INSERT_COMMAND_BASE = "INSERT INTO `players` (`pid`, `first_name`, `last_name`) VALUES ('{pid}', '{f_name}', '{l_name}');"
SQL_SELECT_COMMAND_BASE = "SELECT * FROM `{table}` LIMIT 5"
SQL_INSERT_PLAYER_MATCHES_BASE = '''INSERT INTO `d2matchb_bball`.`player_matches` (
`pid`,
`minutes`,
`points`,
`FGM`,
`FGA`,
`FG%`,
`3PM`,
`3PA`,
`3P%`,
`FTM`,
`FTA`,
`FT%`,
`ORB`,
`DRB`,
`REB`,
`AST`,
`STL`,
`BLK`,
`TOV`,
`PF`,
`mdate`,
`pteam`,
`oteam`,
`home_away`,
`winloss`,
`plusminus`)
VALUES ({pid}, {minutes}, {points}, {fgm}, {fga}, {fgper}, {tpm}, {tpa}, {tpper},
{ftm}, {fta}, {ftper}, {orb}, {drb}, {reb}, {ast}, {stl}, {blk}, {tov}, {pf}, "{mdate}", "{pteam}", "{oteam}", "{home_away}", "{winloss}", {plusminus});'''

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

    def insert_player_match(self, connection, pid, minutes, points, fgm, fga, fgper, tpm, tpa, tpper, ftm, fta, ftper, orb, drb, reb, ast, stl, blk, tov, pf, mdate, pteam, oteam, home_away, winloss, plusminus):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    SQL_INSERT_PLAYER_MATCHES_BASE.format(
                        pid=pid,
                        minutes=minutes,
                        points=points,
                        fgm=fgm,
                        fga=fga,
                        fgper=fgper,
                        tpm=tpm,
                        tpa=tpa,
                        tpper=tpper,
                        ftm=ftm,
                        fta=fta,
                        ftper=ftper,
                        orb=orb,
                        drb=drb,
                        reb=reb,
                        ast=ast,
                        stl=stl,
                        blk=blk,
                        tov=tov,
                        pf=pf,
                        mdate=mdate,
                        pteam=pteam,
                        oteam=oteam,
                        home_away=home_away,
                        winloss=winloss,
                        plusminus=plusminus
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
        self.driver = webdriver.Chrome('{path}/chromedriver'.format(path=os.getcwd()))

    def load_page(self, url):
        self.url = url
        self.driver.get(self.url)
    
    def get_page(self):
        return self.driver.page_source

    # Must call load_page at least once before
    def dom_change_event_class(self, tag_attribute, tag_attribute_value, new_value):
        tag_attr_command = "getElementsByClassName"

        a = 0
        while a < 11:
            try:
                # Need to change the first line of execute_script; [0] hard coded
                self.driver.execute_script('''
                    var el = document.{tag_attr_command}("{tag_attribute_value}")[0];
                    el.value = "{new_value}";
                    var event = document.createEvent("HTMLEvents");
                    event.initEvent("change", true, false);
                    el.dispatchEvent(event);
                '''.format(tag_attr_command=tag_attr_command, tag_attribute_value=tag_attribute_value, new_value=new_value))
                break
                
            except Exception as e:
                time.sleep(1)
                a+=1
                print('Page not loaded, attempt number: {a}'.format(a=a))
                if a < 10:
                    continue

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
        # time.sleep(3)
        print('Gathering player ids for {date}'.format(date=date))

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
            dates.append('{first_date}-{first_digit}{second_digit}'.format(first_date=first_date, first_digit=str(second_date)[2], second_digit=str(second_date)[3]))
            first_date+=1
            second_date+=1
            print(dates)
        
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

    def get_player_matches(self, player_id, date, stat_type, season_type):
        matches_list = []
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
        html = self.get_page()
        soup = BeautifulSoup(html, "html.parser")

        try:
            all_match_rows = soup.tbody.find_all("tr")
        except AttributeError as e:
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
                pteam, oteam = self.get_teams_from_text(match_up.split(" - ")[1])
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
                # NEED TO FIND A WAY TO FIND THIS
                home_away = "H"

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

        for item in matches:
            sql.insert_player_match(
                connection=connection,
                pid=item["pid"],
                minutes=item["minutes"],
                points=item["points"],
                fgm=item["FGM"],
                fga=item["FGA"],
                fgper=item["FG%"],
                tpm=item["3PM"],
                tpa=item["3PA"],
                tpper=item["3P%"],
                ftm=item["FTM"],
                fta=item["FTA"],
                ftper=item["FT%"],
                orb=item["ORB"],
                drb=item["DRB"],
                reb=item["REB"],
                ast=item["AST"],
                stl=item["STL"],
                blk=item["BLK"],
                tov=item["TOV"],
                pf=item["PF"],
                plusminus=item["plusminus"],
                home_away=item["home_away"],
                mdate=item["mdate"],
                pteam=item["pteam"],
                oteam=item["oteam"],
                winloss=item["winloss"]
            )
        sql.close_connection(connection=connection)

    
    def push_all_pmatches_to_db_by_date(self, date, season_type, stat_type, players):
        all_matches = []
        for key, value in players.items():
            pmatches = self.get_player_matches(
                player_id=value,
                date=date,
                season_type=season_type,
                stat_type=stat_type
            )
            self.push_player_matches_to_db(pmatches)
            print('* Records for {key} pushed to db'.format(key=key))


    #Pretty hard-coded
    def get_embedded_text(self, tag):
        for child in tag.descendants:
            if child.string is not None:
                return child.string


    def get_teams_from_text(self, text):
        if 'vs.' in text:
            team1 = text.split('vs.')[0].replace(" ", "")
            team2 = text.split('vs.')[1].replace(" ", "")
        elif '@' in text:
            team1 = text.split('@')[0].replace(" ", "")
            team2 = text.split('@')[1].replace(" ", "")

        return team1, team2


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

    
def single_quote_name(name):
    sname = ""
    if "'" in name:
        sname = name.split("'")[0] + "''" + name.split("'")[1]
        return sname
    sname = name
    return sname

def get_pids(args=None):
    wp = AllPlayerPage()
    try:
        players = wp.get_all_player_ids(
            date=args[2],
            season_type="Regular%20Season",
        )
    except Exception as e:
        raise e

    try:
        if args[3] == '-db':
            wp.push_all_player_ids_to_db(players)
            print("pushed to sql")
        elif args[3] == '-print':
            print(players)
    except Exception as e:
        print("Did you forget the -print modifier?")
        raise e
        
def get_all_pids(args=None):
    wp = AllPlayerPage()
    # Add feature to read season_type with arg
    try:
        players = wp.get_all_player_ids_all_dates(
            season_type="Regular%20Season",
        )
    except Exception as e:
        raise e

    try:
        if args[2] == '-db':
            wp.push_all_player_ids_to_db(players)
            print("pushed to sql")

        elif args[2] == '-print':
            print(players)
    except Exception as e:
        print("Did you forget the -print modifier?")
        raise e
    
# date, season_type, stat_type, players
def get_pmatches(args=None):
    wp = AllPlayerPage()
    pwp = PlayerPage()
    try:
        players = wp.get_all_player_ids(
            date=args[2],
            season_type="Regular%20Season",
        )
        print("Finished gathering player_ids")

        pwp.push_all_pmatches_to_db_by_date(
            date=args[2],
            season_type="Regular%20Season",
            stat_type="boxscores-traditional",
            players=players
        )
    except Exception as e:
        raise e

def main():
    accepted_args = {
        "pids": get_pids,
        "pmatches": get_pmatches,
        "all_pids" : get_all_pids,
    }
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)

    try:
        accepted_args[sys.argv[1]](sys.argv)
    except Exception as e:
        print("Invalid command or modifier")
        raise e
        return

    return


main()
