import os
import time
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from load_config import read_config, set_env_vars
from pymysqlconnect import PyMySQLConn
from webpage import WebPage
from allplayerpage import AllPlayerPage
from playermatchpage import PlayerPage


BASE_PLAYER_URL = "https://stats.nba.com/player/{player_id}/{stat_type}/?Season={date}&SeasonType={season_type}"
BASE_ALL_PLAYER_URL = "https://stats.nba.com/leaders/?Season={date}&SeasonType={season_type}"
TEST_ALL_PLAYER_URL = "https://stats.nba.com/leaders/?Season=2016-17&SeasonType=Regular%20Season"


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
