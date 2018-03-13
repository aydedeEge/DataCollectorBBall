#!/usr/bin/env python3
"""Insert the fake player matches for games to come"""
# -*- encoding: utf-8 -*-
import os,sys,inspect
import MySQLdb

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from load_config import read_config, set_env_vars

def insert_future_match(match_date, team1, team2):
    connection = MySQLdb.connect(host = os.environ["host"],    # your host, usually localhost
                                 user = os.environ["user"],         # your username
                                 passwd = os.environ["pwd"],  # your password
                                 db = os.environ["db"])        # name of the data base

    # you must create a Cursor object. It will let
    # you execute all the queries you need
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    command = "INSERT INTO `d2matchb_bball`.`matches` "
    command += " (`hteam`, `ateam`, `date`)"
    command += "VALUES ('" + team1 + "', '" + team2 + "', '" + match_date + "');"

    cursor.execute(command)
    connection.commit()
    # Close the connection
    connection.close()
    return 0

def get_match_id(match_date, team1, team2):
    connection = MySQLdb.connect(host = os.environ["host"],    # your host, usually localhost
                                 user = os.environ["user"],         # your username
                                 passwd = os.environ["pwd"],  # your password
                                 db = os.environ["db"])        # name of the data base

    # you must create a Cursor object. It will let
    # you execute all the queries you need
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * from matches where date = '" + match_date + " 00:00:00' AND hteam = '" + team1 + "' AND ateam = '" + team2 + "';")
    result = cursor.fetchall()[0]["idmatches"]
    # Close the connection
    connection.close()
    return result

def insert_fake_player_matches(season, match_date, match_id, team1, team2):
    """Insert the fake matches"""
    connection = MySQLdb.connect(host = os.environ["host"],    # your host, usually localhost
                                 user = os.environ["user"],         # your username
                                 passwd = os.environ["pwd"],  # your password
                                 db = os.environ["db"])        # name of the data base

    # you must create a Cursor object. It will let
    # you execute all the queries you need
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM player_stats WHERE (team = '" + team1 + "' OR team = '" + team2 + "') AND season = '" + season + "';")
    result_set = cursor.fetchall()
    value_command = "VALUES "
    match_date_no_hyphens = match_date.replace("-", "")
    for row in result_set:
        pid = row["player_id"] 
        player_match_id = match_date_no_hyphens + str(pid)
        mdate = match_date
        if(team1 == row["team"]):
            pteam = team1
            oteam = team2
            home_away = "H"
        else:
            pteam = team2
            oteam = team1
            home_away = "A"
        value_command += " ('" + player_match_id + "', '" + str(pid) + "', '" + match_id + "', '" + mdate + "', '" + pteam + "', '" + oteam + "', '" + home_away + "'),"

    value_command = value_command[:-1] + ";"
    command = "INSERT INTO `d2matchb_bball`.`player_matches` "
    command += "(`player_match_id`, `pid`, `match_id`, `mdate`, `pteam`, `oteam`, `home_away`) "
    command += value_command

    cursor.execute(command)
    connection.commit()
    # Close the connection
    connection.close()
    return 0

if __name__ == '__main__':
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)
    insert_future_match("2018-03-13", "MIN", "WAS")
    mid = get_match_id("2018-03-13", "MIN", "WAS")
    insert_fake_player_matches("2017", "2018-03-13", str(mid), "MIN", "WAS")
