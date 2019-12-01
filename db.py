import pymysql
import pymysql.cursors
from datetime import datetime

class Database(object):

    def __init__(self):
        self.conn = pymysql.connect('sql10.freesqldatabase.com', 'sql10312094', 'QSxqniDfqx', 'sql10312094', charset = 'utf8mb4')
        self.cur = self.conn.cursor()

    def getAnimeList(self, id):

        self.cur.execute("SELECT id, nome, diretorio FROM obras INNER JOIN animes ON id = idObra WHERE upado = 0 AND idUsuario = {}".format(id))
        rows = self.cur.fetchall()

        return rows

    def getUser(self):

        self.cur.execute("SELECT id, login, senha FROM usuarios WHERE up = 1")
        rows = self.cur.fetchall()

        return rows

    def insertAnime(self, anime):

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(date)
        self.cur.execute("INSERT INTO episodios (idUsuario, idObra, nome, numero, duracao, thumb, nomeArquivo, qualidadeMax, temporada, dataPostagem, views) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(anime.userId, anime.animeId, anime.args['nome'], anime.args['episodio'], anime.args['duracao'], anime.args['thumb'], anime.fileName, anime.args['qualidade'], anime.args['temporada'], date, 0))

        self.conn.commit()

    def __del__(self):
        self.conn.close()
