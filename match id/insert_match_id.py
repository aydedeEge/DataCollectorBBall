#!/usr/bin/env python3
"""Insert the match ID into the player matches table"""
# -*- encoding: utf-8 -*-
import os,sys,inspect
import MySQLdb
import time

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from load_config import read_config, set_env_vars


# TODO: if it already exists, update the score instead of throwing dup key error
def find_and_insert(limit):
    """Find and insert the match ID."""
    connection = MySQLdb.connect(host = os.environ["host"],    # your host, usually localhost
                                 user = os.environ["user"],         # your username
                                 passwd = os.environ["pwd"],  # your password
                                 db = os.environ["db"])        # name of the data base

    # you must create a Cursor object. It will let
    # you execute all the queries you need
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    #three step process
    #1. Get all of the desired player_matches rows and store the home, away, and date
    #2. Go through all of the stored homes, aways, and dates, and find the match ID
    #3. Go back through the player_matches rows and update the values as desired.

    #1.We get the desired. 
    cursor.execute("SELECT * FROM player_matches where match_id is NULL LIMIT " + str(limit) + ";")
    player_matches_result_set = cursor.fetchall()
    player_match_ids = {}
    pm_unique_keys = {}
    homes = {}
    aways = {}
    dates = {}
    if(len(player_matches_result_set) != 0):
        for row in player_matches_result_set:
            player_match_id = str(row["player_match_id"])
            if(row["home_away"] == "H"):
                home = (row["pteam"])
                away = (row["oteam"])
            else:
                home = (row["oteam"])
                away = (row["pteam"])
            date = str(row["mdate"])
            homes[player_match_id] = home
            aways[player_match_id] = away
            dates[player_match_id] = date + " 00:00:00"
            un_key = str(home) + str(away) + str(date)
            pm_unique_keys[player_match_id] = un_key
            #we have a dictionary of player match IDs that uses the home, away, and date as the key.
            player_match_ids[un_key] = player_match_id
            
        team_and_date_conditions = ""
        #2. We find the match IDs in one call
        for pm_id in homes:
            team_and_date_conditions += "(hteam='" + homes[pm_id] + "' and ateam='" + aways[pm_id] + "' and date='" + dates[pm_id] + "') OR "
        command = "SELECT * FROM matches where " + team_and_date_conditions[:-4] + ";"
        cursor.execute(command)
        matches_result_set = cursor.fetchall()

        matches = {}
        for row in matches_result_set:
            home = str(row["hteam"])
            away = str(row["ateam"])
            date = str(row["date"])[:-9]
            matches[home + away + date] = row["idmatches"]
        
        #we now have match IDs for each unique key (where a key is home, away, and date
        
        # 3. now we can go through and create an update command
        when_conditional = ""
        when_list = ""
        for row in player_matches_result_set:
            player_match_id = str(row["player_match_id"])
            unique_key = pm_unique_keys[player_match_id]
            when_conditional += "WHEN '" + str(player_match_id) + "' THEN '" + str(matches[unique_key]) + "' "
            when_list += "'" + str(player_match_id) + "',"

        print("Total IDs to be inserted = " + str(len(player_matches_result_set)))

        command = "UPDATE `d2matchb_bball`.`player_matches` SET match_id = CASE player_match_id "
        command += when_conditional + "ELSE match_id END WHERE player_match_id IN(" + when_list[:-1] + ");"
        cursor.execute(command)
        connection.commit()
        # Close the connection
        connection.close()
        return 0
    else:
        print("No Null match IDs found for those criteria")
        connection.close()
        return -1


if __name__ == '__main__':
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)
    max_range = 10
    batch_size = 200
    start_time = time.time()
    if(len(sys.argv) > 1):
        max_range = sys.argv[1]
    if(len(sys.argv) > 2):
        batch_size = sys.argv[2]
    for i in range(0,int(max_range)):
        find_and_insert(batch_size)
    res = 0
    total_time = time.time() - start_time
    secs_per_item = total_time / (int(batch_size)*int(max_range))
    print("It took " + str(1000*secs_per_item) + " milliseconds per item")