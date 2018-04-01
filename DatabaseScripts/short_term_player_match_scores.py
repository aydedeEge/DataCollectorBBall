#!/usr/bin/env python3
"""Calculate the match scores"""
# -*- encoding: utf-8 -*-
import os,sys,inspect
import MySQLdb

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from load_config import read_config, set_env_vars


# TODO: if it already exists, update the score instead of throwing dup key error
FG_3_SCORE = 3
FG_SCORE = 2
FT_SCORE = 1
RB_SCORE = 1.2
AST_SCORE = 1.5
BLK_SCORE = 3
STEAL_SCORE = 3
TURNOVER_SCORE = -1
SEASON = 2017
N_PREVIOUS = 5

def last_n_average(values, n):
    average = 0.
    value_size = len(values)
    count = 0
    while(value_size - count - 1 >= 0 and count < n):
        average += values[value_size - count - 1]
        count += 1
    
    if(count > 0):
        return average / float(count)
    else:
        return 0

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
        if(row["short_score_5"] == None):
            curr_score = last_n_average(game_scores, N_PREVIOUS)
            when_conditional += "WHEN '" + str(player_match_id) + "' THEN '" + str(curr_score) + "' "
            when_list += "'" + str(player_match_id) + "',"
        game_scores.append(row["score"])
        

    print("Total short_scores calculated = " + str(len(result_set)))
    if(len(result_set) != 0):
        command = "UPDATE `d2matchb_bball`.`player_matches` SET short_score_5 = CASE player_match_id "
        command += when_conditional + "ELSE short_score_5 END WHERE player_match_id IN(" + when_list[:-1] + ");"
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
    command = "SELECT distinct(pid) FROM player_matches WHERE pid NOT IN (SELECT pid FROM player_matches WHERE short_score_5 is not null) limit " + str(limit) + ";"
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
    command = "SELECT distinct(pid) FROM player_matches WHERE pid IN (SELECT pid FROM player_matches WHERE short_score_5 is null) limit " + str(limit) + ";"
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
        
