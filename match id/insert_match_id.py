#!/usr/bin/env python3
"""Insert the match ID into the player matches table"""
# -*- encoding: utf-8 -*-
import os,sys,inspect
import MySQLdb

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from load_config import read_config, set_env_vars


# TODO: if it already exists, update the score instead of throwing dup key error

def find_and_insert():
    """Find and insert the match ID."""
    connection = MySQLdb.connect(host = os.environ["host"],    # your host, usually localhost
                                 user = os.environ["user"],         # your username
                                 passwd = os.environ["pwd"],  # your password
                                 db = os.environ["db"])        # name of the data base

    # you must create a Cursor object. It will let
    # you execute all the queries you need
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM player_matches where match_id is NULL and mdate like '2017-01-%';")
    result_set = cursor.fetchall()

    pmids = []
    update_command_string = """UPDATE `d2matchb_bball`.`player_matches` SET match_id = CASE player_match_id """
    
    for row in result_set:
        pmid = row["player_match_id"]
        pmids.append(pmid)
        if(row["home_away"] == "H"):
            home = (row["pteam"])
            away = (row["oteam"])
        else:
            home = (row["oteam"])
            away = (row["pteam"])
        date = str(row["mdate"]) + " 00:00:00"

        cursor.execute("SELECT * FROM matches where hteam = \"" + home + "\" and ateam =\"" + away + \
        "\" and date =\"" + date + "\";")
        new_results = cursor.fetchall()
        if(new_results[0] is not None):
            match_id = new_results[0]["idmatches"]
            print(match_id)
            update_command_string += "WHEN " + str(pmid) + " THEN " + str(match_id) + " "
            #cursor.execute("UPDATE `d2matchb_bball`.`player_matches` SET `match_id`='" + str(match_id) +\
            # "' WHERE `player_match_id`='" + str(pmid) + "';")
    
    update_command_string += "ELSE match_id END WHERE player_match_id IN ("
    isEmpty = 1
    for pmid in pmids:
        update_command_string += str(pmid) + ","
        isEmpty = 0
    update_command_string = update_command_string[:-1] + ");"
    if(isEmpty == 0):
        cursor.execute(update_command_string)
    connection.commit()
    # print all the first cell of all the rows
    connection.close()

if __name__ == '__main__':
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)

    find_and_insert()
