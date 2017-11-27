#!/usr/bin/env python3
"""Calculate the scores"""
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

    # get the player_stats items that don't have a score
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM player_stats where score is null limit " + str(limit) + ";")
    result_set = cursor.fetchall()

    if(len(result_set) > 0):
        when_conditional = ""
        when_list = ""
        # in our for loop, we append to a single SQL command to update all scores in this batch at once
        for row in result_set:
            score = (row["FG_36"] * FG_SCORE + row["3P_36"] * FG_3_SCORE + row["FT_36"] * FT_SCORE +\
                    row["TRB_36"] * RB_SCORE + row["AST_36"] * AST_SCORE + row["BLK_36"] * BLK_SCORE +\
                    row["STL_36"] * STEAL_SCORE + row["TOV_36"] * TURNOVER_SCORE)
            player_stats_id = row["player_stats_id"]
            when_conditional += "WHEN '" + str(player_stats_id) + "' THEN '" + str(score) + "' "
            when_list += "'" + str(player_stats_id) + "',"
        #make and execute that command.
        command = "UPDATE `d2matchb_bball`.`player_stats` SET score = CASE player_stats_id "
        command += when_conditional + "ELSE score END WHERE player_stats_id IN(" + when_list[:-1] + ");"
        cursor.execute(command)
        connection.commit()
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
    count = 0
    # goes through until all scores are done.
    while(res == 0):
        res = calculate(100)
        count = count + 1
        print("done batch " + str(count))
