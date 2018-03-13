#!/usr/bin/env python3
"""Insert the future player matches for games to come"""
# -*- encoding: utf-8 -*-
import os,sys,inspect
import MySQLdb
import pandas as pd

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
    try:
        cursor.execute(command)
        connection.commit()
    except:
        print("Something went wrong when adding match")
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

def insert_future_player_matches(season, match_date, fd_data):
    """Insert the future matches"""
    connection = MySQLdb.connect(host = os.environ["host"],    # your host, usually localhost
                                 user = os.environ["user"],         # your username
                                 passwd = os.environ["pwd"],  # your password
                                 db = os.environ["db"])        # name of the data base

    # you must create a Cursor object. It will let
    # you execute all the queries you need
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    
    #first we need to gather all of the player ids
    player_ids = {} #indexed by first and last name
    first_names = fd_data["First Name"]
    last_names = fd_data["Last Name"]

    or_conditional = ""
    for i in range(len(first_names)):
        or_conditional += "(first_name = " + first_names[i] + " and last_name = " + last_names[i] + ") OR"

    command = "SELECT * from players where " + or_conditional[:-3] + ";"
    for row in fd_data:

    
    
    
    
    
    
    value_command = "VALUES "
    match_date_no_hyphens = match_date.replace("-", "")
    




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

def insert_future_matches(games, game_date):
    added_matches = []
    ateams = {}
    hteams = {}
    for g in games:
        if(g not in added_matches):
            added_matches.append(g)
            ateam = g.split("@")[0]
            hteam = g.split("@")[1]
            ateam = fix_team(ateam)
            hteam = fix_team(hteam)
            ateams[g] = ateam
            hteams[g] = hteam
            insert_future_match(game_date, hteam, ateam)
    return added_matches, hteams, ateams
def fix_team(team):
    if(len(team) == 3):
        return team
    else:
        if(team == "NY"):
            return "NYK"
        elif(team == "NO"):
            return "NOP"
        elif(team == "SA"):
            return "SAS"
        else:
            print("ERROR: Team unknown (" + team + ")")

if __name__ == '__main__':
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)
    game_date = "2018-03-13"
    competition_number = "24098"
    season = "2017"
    filename = "DatabaseScripts/FanDuel/FanDuel-NBA-" + game_date + "-" + competition_number + "-players-list.csv"
    fd_data = pd.read_csv(filename)
    #print(fd_data["Game"])
    matches, hteams, ateams = insert_future_matches(fd_data["Game"], game_date)
    
    match_ids = {}
    for m in matches:
        match_ids[m] = get_match_id(game_date, hteams[m], ateams[m])
    
    #now we have the match IDs, we go through them and add the player matches
    for m in matches:
        mid = match_ids[m]
        insert_future_player_matches(season, game_date, fd_data)
