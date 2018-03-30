#!/usr/bin/env python3
"""Insert the future player matches for games to come"""
# -*- encoding: utf-8 -*-
import os,sys,inspect
import MySQLdb
import pandas as pd
import math

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

def insert_future_player_matches(season, match_date, match_ids, fd_data, update_injuries):
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
        if(isinstance(first_names[i], float)):
            # This covers Nene
            or_conditional += " (first_name = \"" + last_names[i] + "\") OR"
        else:
            or_conditional += " (first_name = \"" + first_names[i] + "\" and last_name = \"" + fix_name(last_names[i]) + "\") OR"
    
    command = "SELECT * from players where" + or_conditional[:-3] + ";"
    #print(command)
    cursor.execute(command)
    cursor_result = cursor.fetchall()
    for row in cursor_result:
        player_ids[row["first_name"] + row["last_name"]] = row["pid"]
    
    value_command = "VALUES "
    match_date_no_hyphens = match_date.replace("-", "")
    used_pids = []
    #now we have player ids, go through the data
    for index, row in fd_data.iterrows():
        first_name = str(row["First Name"])
        last_name = fix_name(str(row["Last Name"]))
        key_name = first_name + last_name
        if key_name in player_ids:
            pid = player_ids[first_name + last_name]
            player_match_id = match_date_no_hyphens + str(pid)
            mdate = match_date
            pteam = fix_team(row["Team"])
            oteam = fix_team(row["Opponent"])
            match_id = match_ids[row["Game"]]
            salary = row["Salary"]
            position = row["Position"]
            if(str(row["Team"]) + "@" + str(row["Opponent"]) == row["Game"]):
                home_away = "A"
            else:
                home_away = "H"
            injury = row["Injury Indicator"]
            value_command += " ('" + player_match_id + "', '" + str(pid) + "', '" + str(match_id) + "', '" + str(mdate) + "', '" + pteam + "', '" + oteam + "', '" + home_away + "', '" + str(salary) + "', '" + position + "', '" + str(injury) + "'),"
        else:
            print("Not in db: " + key_name)
    value_command = value_command[:-1] + ";"
    command = "INSERT INTO `d2matchb_bball`.`player_matches` "
    command += "(`player_match_id`, `pid`, `match_id`, `mdate`, `pteam`, `oteam`, `home_away`, `salary`, `daily_pos`,`injury`) "
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

def fix_name(name):
    return name.replace(" Jr.", "").replace(" III", "").replace(" II", "")

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
        elif(team == "GS"):
            return "GSW"
        else:
            print("ERROR: Team unknown (" + team + ")")

if __name__ == '__main__':
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)
    game_date = "2018-03-30"
    competition_number = "24511"
    season = "2017"
    filename = "DatabaseScripts/FanDuel/FanDuel-NBA-" + game_date + "-" + competition_number + "-players-list.csv"
    fd_data = pd.read_csv(filename)
    matches, hteams, ateams = insert_future_matches(fd_data["Game"], game_date)
    
    match_ids = {}
    for m in matches:
        match_ids[m] = get_match_id(game_date, hteams[m], ateams[m])
    
    #now we have the match IDs, we go through them and add the player matches
    insert_future_player_matches(season, game_date, match_ids, fd_data, False)
