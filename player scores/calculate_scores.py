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

def calculate():
    """Calculate the scores"""
    connection = MySQLdb.connect(host = os.environ["host"],    # your host, usually localhost
                                 user = os.environ["user"],         # your username
                                 passwd = os.environ["pwd"],  # your password
                                 db = os.environ["db"])        # name of the data base

    # you must create a Cursor object. It will let
    # you execute all the queries you need
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM player_stats")
    result_set = cursor.fetchall()

    for row in result_set:
        score = (row["FG_36"] * FG_SCORE + row["3P_36"] * FG_3_SCORE + row["FT_36"] * FT_SCORE +\
                 row["TRB_36"] * RB_SCORE + row["AST_36"] * AST_SCORE + row["BLK_36"] * BLK_SCORE +\
                 row["STL_36"] * STEAL_SCORE + row["TOV_36"] * TURNOVER_SCORE)
        player_id = row["player_id"]

        cursor.execute("INSERT INTO `d2matchb_bball`.`scores` (`player_id`, `season`, `score`)" +\
                       " VALUES (" + str(player_id) + "," + str(SEASON) + "," + str(score) + ");")

    connection.commit()
    # print all the first cell of all the rows
    connection.close()

if __name__ == '__main__':
    # Db config initialization
    conf = read_config()
    set_env_vars(conf)

    calculate()
