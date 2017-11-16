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

def calculate(limit):
    """Calculate the scores"""
    connection = MySQLdb.connect(host = os.environ["host"],    # your host, usually localhost
                                 user = os.environ["user"],         # your username
                                 passwd = os.environ["pwd"],  # your password
                                 db = os.environ["db"])        # name of the data base

    # you must create a Cursor object. It will let
    # you execute all the queries you need
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM player_matches where score is null and match_id is not null LIMIT " + str(limit) + ";")
    result_set = cursor.fetchall()
    scores = {}
    when_conditional = ""
    when_list = ""
    for row in result_set:
        curr_score = (row["FGM"] * FG_SCORE + row["3PM"] * FG_3_SCORE + row["FTM"] * FT_SCORE +\
                 row["REB"] * RB_SCORE + row["AST"] * AST_SCORE + row["BLK"] * BLK_SCORE +\
                 row["STL"] * STEAL_SCORE + row["TOV"] * TURNOVER_SCORE)
        player_match_id = str(row["player_match_id"])
        scores[player_match_id] = curr_score
        when_conditional += "WHEN '" + str(player_match_id) + "' THEN '" + str(curr_score) + "' "
        when_list += "'" + str(player_match_id) + "',"

    print("Total scores calculated = " + str(len(result_set)))
    if(len(result_set) != 0):
        command = "UPDATE `d2matchb_bball`.`player_matches` SET score = CASE player_match_id "
        command += when_conditional + "ELSE score END WHERE player_match_id IN(" + when_list[:-1] + ");"
        cursor.execute(command)
        connection.commit()
        # Close the connection
        connection.close()
        return 0
    else:
        connection.close()
        return -1


if __name__ == '__main__':
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)

    res = 0
    while(res != -1):
        res = calculate(250)