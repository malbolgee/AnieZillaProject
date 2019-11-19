import pymysql
import pymysql.cursors
from datetime import datetime

class Database(object):

    def __init__(self):
        self.conn = pymysql.connect('sql10.freesqldatabase.com', 'sql10312094', 'QSxqniDfqx', 'sql10312094', charset = 'utf8mb4')
        self.cur = self.conn.cursor()

    def fetch(self, table):
        self.cur.execute('SELECT * FROM {}'.format(table))
        rows = self.cur.fetchone()

        desctiption = self.cur.description

        return rows

    def getAnimeList(self, id, name):

        self.cur.execute("SELECT id, nome, diretorio FROM obras INNER JOIN animes ON id = idObra WHERE upado = 0 AND idUsuario = {} AND nome LIKE '%{}%'".format(id, name))
        rows = self.cur.fetchall()

        return rows

    def formartString(self, string):

        for i in range(len(string) - 1):
            string[i] = string[i] + ', '

        return string

    def getUser(self):

        self.cur.execute("SELECT id, login, senha FROM usuarios WHERE up = 1")
        rows = self.cur.fetchall()

        return rows

    def insert(self, table, columns, *values):

        if table == 'episodios':
            self.cur.execute("INSERT INTO episodios " + "(" + columns + ")" + " VALUES ('{}', '{}', '{}', '{}', '{}', '{}, '{}', '{}, '{}', '{}', '{}')".format(*values))
        elif table == 'obras':
            self.cur.execute("INSERT INTO obras " + "(" + columns + ")" + " VALUES ('{}', '{}', '{}', '{}', '{}', '{}, '{}', '{}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}, '{}', '{}, '{}')".format(*values))

        self.conn.commit()

    def __del__(self):
        self.conn.close()
