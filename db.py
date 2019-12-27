import pymysql
import pymysql.cursors
from datetime import datetime

class Database(object):

    # def __init__(self):
        # self.conn = pymysql.connect('aniedb.mysql.dbaas.com.br', 'aniedb', 'starred1234', 'aniedb', charset = 'utf8mb4')
        # self.cur = self.conn.cursor()

    def getAnimeList(self, id):
        
        self.conn = pymysql.connect('aniedb.mysql.dbaas.com.br', 'aniedb', 'starred1234', 'aniedb', charset = 'utf8mb4')
        self.cur = self.conn.cursor()

        self.cur.execute("SELECT id, nome, diretorio FROM obras INNER JOIN animes ON id = idObra WHERE upado = 0 AND idUsuario = {}".format(id))
        rows = self.cur.fetchall()

        self.conn.close()

        return rows

    def getUser(self):

        self.conn = pymysql.connect('aniedb.mysql.dbaas.com.br', 'aniedb', 'starred1234', 'aniedb', charset = 'utf8mb4')
        self.cur = self.conn.cursor()

        self.cur.execute("SELECT id, login, senha FROM usuarios WHERE up = 1")
        rows = self.cur.fetchall()

        self.conn.close()

        return rows

    def insertAnime(self, anime):

        self.conn = pymysql.connect('aniedb.mysql.dbaas.com.br', 'aniedb', 'starred1234', 'aniedb', charset = 'utf8mb4')
        self.cur = self.conn.cursor()

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute("INSERT INTO episodios (idUsuario, idObra, nome, numero, duracao, thumb, nomeArquivo, qualidadeMax, temporada, dataPostagem, views) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(anime.userId, anime.animeId, anime.args['nome'], anime.args['episodio'], anime.args['duracao'], anime.args['thumb'], anime.fileName, anime.args['qualidade'], anime.args['temporada'], date, 0))
        self.conn.commit()

        self.conn.close()
    
    def isRepeated(self, id, number):

        self.conn = pymysql.connect('aniedb.mysql.dbaas.com.br', 'aniedb', 'starred1234', 'aniedb', charset = 'utf8mb4')
        self.cur = self.conn.cursor()

        self.cur.execute("SELECT * FROM episodios WHERE idObra = {} and numero = {}".format(id, number))
        
        result = self.cur.fetchone()

        self.conn.close()

        return result

# db = Database()

# print(db.isRepeated(186, 1))