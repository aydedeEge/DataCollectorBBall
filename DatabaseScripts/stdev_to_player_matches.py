#!/usr/bin/env python3
"""Calculate the standard deviation"""
# -*- encoding: utf-8 -*-
import os,sys,inspect
import MySQLdb
import numpy as np

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from load_config import read_config, set_env_vars

SEASON = 2017
N_PREVIOUS = 10

def last_n_stdev(values, n):
    if(len(values) < 2):
        return 0
    elif(len(values) < n):
        return np.std(values, ddof=1)
    else:
        var_values = []
        for i in range(0, n):
            var_values.append(values[len(values)-1-i])
        return np.std(var_values, ddof=1)

def calculate(player_id):
    """Calculate the scores"""
    connection = MySQLdb.connect(host = os.environ["host"],    # your host, usually localhost
                                 user = os.environ["user"],         # your username
                                 passwd = os.environ["pwd"],  # your password
                                 db = os.environ["db"])        # name of the data base

    # you must create a Cursor object. It will let
    # you execute all the queries you need
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM player_matches where pid = " + str(player_id) + " order by mdate;")
    result_set = cursor.fetchall()
    game_scores = []

    when_conditional = ""
    when_list = ""

    for row in result_set:
        player_match_id = str(row["player_match_id"])
        #only update if it's nothing...
        if(row["stdev_10"] == None):
            curr_stdev = last_n_stdev(game_scores, N_PREVIOUS)
            when_conditional += "WHEN '" + str(player_match_id) + "' THEN '" + str(curr_stdev) + "' "
            when_list += "'" + str(player_match_id) + "',"
        game_scores.append(row["score"])

    print("Total standard deviations calculated = " + str(len(result_set)))
    if(len(result_set) != 0):
        command = "UPDATE `d2matchb_bball`.`player_matches` SET stdev_10 = CASE player_match_id "
        command += when_conditional + "ELSE stdev_10 END WHERE player_match_id IN(" + when_list[:-1] + ");"
        cursor.execute(command)
        connection.commit()
        # Close the connection
        connection.close()
        return 0
    else:
        connection.close()
        return -1

def get_player_ids(limit):
    connection = MySQLdb.connect(host = os.environ["host"],    # your host, usually localhost
                                 user = os.environ["user"],         # your username
                                 passwd = os.environ["pwd"],  # your password
                                 db = os.environ["db"])        # name of the data base
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    command = "SELECT distinct(pid) FROM player_matches WHERE pid NOT IN (SELECT pid FROM player_matches WHERE stdev_10 is not null) limit " + str(limit) + ";"
    cursor.execute(command)
    result_set = cursor.fetchall()
    result = []
    for row in result_set:
        result.append(row["pid"])    
    connection.close()
    return result


def get_player_ids_to_append(limit):
    connection = MySQLdb.connect(host = os.environ["host"],    # your host, usually localhost
                                 user = os.environ["user"],         # your username
                                 passwd = os.environ["pwd"],  # your password
                                 db = os.environ["db"])        # name of the data base
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    command = "SELECT distinct(pid) FROM player_matches WHERE pid IN (SELECT pid FROM player_matches WHERE stdev_10 is null) limit " + str(limit) + ";"
    cursor.execute(command)
    result_set = cursor.fetchall()
    result = []
    for row in result_set:
        result.append(row["pid"])    
    connection.close()
    return result

if __name__ == '__main__':
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)
    ids_to_update = get_player_ids_to_append(300)
    count = 0
    for pid in ids_to_update:
        res = calculate(pid)
        count+=1
        print("done " + str(count) + "/" + str(len(ids_to_update)))
        
