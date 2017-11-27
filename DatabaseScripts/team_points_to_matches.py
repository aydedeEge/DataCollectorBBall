#!/usr/bin/env python3
"""Insert the match ID into the player matches table"""
# -*- encoding: utf-8 -*-
import os,sys,inspect
import MySQLdb

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from load_config import read_config, set_env_vars


def calculate_and_insert(limit):
    """Calculate the team points and insert into the matches table"""
    connection = MySQLdb.connect(host = os.environ["host"], user = os.environ["user"], passwd = os.environ["pwd"], db = os.environ["db"])

    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    
    #three step process
    #1. Get all of the desired matches
    #2. Grab all the relevant player_matches
    #3. Calculate the scores for each team
    #4. Update the matches table

    #1. Get the desired matches (ordered by most recent)
    command = "SELECT * FROM matches where hteam_points is null and date < '2017-06-01' order by date desc LIMIT " + str(limit) + ";"
    cursor.execute(command)
    
    matches_result_set = cursor.fetchall()
    match_ids = []
    pm_command = "SELECT * FROM player_matches WHERE "
    if(len(matches_result_set) != 0):
        # First get the match IDs that we want.
        for row in matches_result_set:
            pm_command += "match_id = " + str(row["idmatches"]) + " OR "
            match_ids.append(str(row["idmatches"]))

        # get all the player matches
        pm_command = pm_command[:-4] + ";"
        cursor.execute(pm_command)
        player_matches_result_set = cursor.fetchall()
        if(len(player_matches_result_set) > 0):
            home_scores = {}
            away_scores = {}
            
            for row in player_matches_result_set:
                curr_key = str(int(row["match_id"]))
                if(row["home_away"] == "H"):
                    if curr_key in home_scores:
                        home_scores[curr_key] += int(row["points"])
                    else:
                        home_scores[curr_key] = int(row["points"])
                else:
                    if curr_key in away_scores:
                        away_scores[curr_key] += int(row["points"])
                    else:
                        away_scores[curr_key] = int(row["points"])
            #home team
            when_conditional = ""
            when_list = ""
            for m_id in match_ids:
                if m_id in home_scores:
                    when_conditional += "WHEN " + m_id + " THEN " + str(home_scores[m_id]) + " "
                    when_list += m_id + ","

            command = "UPDATE `d2matchb_bball`.`matches` SET hteam_points = CASE idmatches "
            command += when_conditional + "ELSE hteam_points END WHERE idmatches IN(" + when_list[:-1] + ");"
            cursor.execute(command)

            #away team
            when_conditional = ""
            when_list = ""
            for m_id in match_ids:
                if m_id in away_scores:
                    when_conditional += "WHEN " + m_id + " THEN " + str(away_scores[m_id]) + " "
                    when_list += m_id + ","

            command = "UPDATE `d2matchb_bball`.`matches` SET ateam_points = CASE idmatches "
            command += when_conditional + "ELSE ateam_points END WHERE idmatches IN(" + when_list[:-1] + ");"
            cursor.execute(command)

            connection.commit()
            # Close the connection
            connection.close()
            return 0
        else:
            print("Those match IDs did not have corresponding player_match entries")
            return -1
    else:
        connection.close()
        return -1


if __name__ == '__main__':
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)

    res = 0
    while(res != -1):
        res = calculate_and_insert(100)
        if(res == 0):
            print("Inserted scores for 100 matches...")
