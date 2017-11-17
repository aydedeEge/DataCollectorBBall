import pymysql

SQL_INSERT_COMMAND_BASE = "INSERT INTO `players` (`pid`, `first_name`, `last_name`) VALUES ('{pid}', '{f_name}', '{l_name}');"
SQL_SELECT_COMMAND_BASE = "SELECT * FROM `{table}` LIMIT 5"
SQL_INSERT_PLAYER_MATCHES_BASE = '''INSERT INTO `d2matchb_bball`.`player_matches` (
`pid`,
`minutes`,
`points`,
`FGM`,
`FGA`,
`FG%`,
`3PM`,
`3PA`,
`3P%`,
`FTM`,
`FTA`,
`FT%`,
`ORB`,
`DRB`,
`REB`,
`AST`,
`STL`,
`BLK`,
`TOV`,
`PF`,
`mdate`,
`pteam`,
`oteam`,
`home_away`,
`winloss`,
`plusminus`)
VALUES ({pid}, {minutes}, {points}, {fgm}, {fga}, {fgper}, {tpm}, {tpa}, {tpper},
{ftm}, {fta}, {ftper}, {orb}, {drb}, {reb}, {ast}, {stl}, {blk}, {tov}, {pf}, "{mdate}", "{pteam}", "{oteam}", "{home_away}", "{winloss}", {plusminus});'''

SQL_INSERT_MATCHES_BASE = """INSERT INTO `d2matchb_bball`.`matches`(`hteam`,`ateam`,`winner`,`date`) VALUES ("{hteam}", "{ateam}", "{winner}", "{date}");"""
SQL_INSERT_TEAM_BASE = """INSERT INTO `d2matchb_bball`.`teams` (`teamid`, `name`) VALUES ({teamid}, "{name}");"""


class PyMySQLConn:
    def __init__(self, config):
        self.host = config.get("host")
        self.user = config.get("user")
        self.pwd = config.get("pwd")
        self.db = config.get("db")

    def reset_config(self, config):
        pass

    def connect_db(self):
        connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.pwd,
            db=self.db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        return connection

    def execute_command(self, connection, command):
        try:
            with connection.cursor() as cursor:
                cursor.execute(command)
            connection.commit()
        except Exception as e:
            raise e

    def insert_players_command(self, connection, pid, f_name, l_name):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    SQL_INSERT_COMMAND_BASE.format(
                        pid=pid,
                        f_name=f_name,
                        l_name=l_name
                    )
                )
            connection.commit()
        except Exception as e:
            raise e

    def insert_player_matches(self, connection, matches):
        cursor = connection.cursor()
        columns = "(`pid`,`minutes`,`points`,`FGM`,`FGA`,`FG%`,`3PM`,`3PA`,`3P%`,`FTM`,`FTA`,`FT%`,`ORB`,`DRB`,`REB`,`AST`,`STL`,`BLK`,`TOV`,`PF`,`mdate`,`pteam`,`oteam`,`home_away`,`winloss`,`plusminus`)"
        command = "INSERT INTO `d2matchb_bball`.`player_matches` " + columns + " VALUES "
        value_strings = []
        for m in matches:
            value_strings.append("('" + str(m["pid"]) + "','" + str(m["minutes"]) + "','" + str(m["points"]) + "','" + str(m["FGM"]) +\
            "','" + str(m["FGA"]) + "','" + str(m["FG%"]) + "','" + str(m["3PM"]) + "','" + str(m["3PA"]) + "','" + str(m["3P%"]) +\
            "','" + str(m["FTM"]) + "','" + str(m["FTA"]) + "','" + str(m["FT%"]) + "','" + str(m["ORB"]) +\
            "','" + str(m["DRB"]) + "','" + str(m["REB"]) + "','" + str(m["AST"]) + "','" + str(m["STL"]) + "','" + str(m["BLK"]) +\
            "','" + str(m["TOV"]) + "','" + str(m["PF"]) + "','" + str(m["mdate"]) + "','" + str(m["pteam"]) + "','" + str(m["oteam"]) +\
            "','" + str(m["home_away"]) + "','" + str(m["winloss"]) + "','" + str(m["plusminus"]) + "')")
        value_string = ""
        for vs in value_strings:
            value_string += vs + ","
        value_string = value_string[:-1]

        command += value_string + ";"
        cursor.execute(command)
        connection.commit()

    def insert_player_match(self, connection, pid, minutes, points, fgm, fga, fgper, tpm, tpa, tpper, ftm, fta, ftper, orb, drb, reb, ast, stl, blk, tov, pf, mdate, pteam, oteam, home_away, winloss, plusminus):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    SQL_INSERT_PLAYER_MATCHES_BASE.format(
                        pid=pid,
                        minutes=minutes,
                        points=points,
                        fgm=fgm,
                        fga=fga,
                        fgper=fgper,
                        tpm=tpm,
                        tpa=tpa,
                        tpper=tpper,
                        ftm=ftm,
                        fta=fta,
                        ftper=ftper,
                        orb=orb,
                        drb=drb,
                        reb=reb,
                        ast=ast,
                        stl=stl,
                        blk=blk,
                        tov=tov,
                        pf=pf,
                        mdate=mdate,
                        pteam=pteam,
                        oteam=oteam,
                        home_away=home_away,
                        winloss=winloss,
                        plusminus=plusminus
                    )
                )
            connection.commit()
        except Exception as e:
            raise e
    
    def insert_match(self, connection, hteam, ateam, winner, date):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    SQL_INSERT_MATCHES_BASE.format(
                        hteam=hteam,
                        ateam=ateam,
                        winner=winner,
                        date=date,
                    )
                )
            connection.commit()
        except Exception as e:
            raise e

    def insert_team(self, connection, teamid, name):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    SQL_INSERT_TEAM_BASE.format(
                        teamid=teamid,
                        name=name,
                    )
                )
            connection.commit()
        except Exception as e:
            raise e

    def select_from_table_command(self, connection, table):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    SQL_SELECT_COMMAND_BASE.format(
                        table=table
                    )
                )
        except Exception as e:
            raise e

    def commit_changes(self, connection):
        connection.commit()

    def close_connection(self, connection):
        connection.close()