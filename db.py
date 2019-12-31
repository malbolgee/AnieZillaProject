import pymysql
import pymysql.cursors
from constants import *

class Database(object):

    def getAnimeList(self, userId):
        """ Returns a list of animes that are not completed yet. """
        
        self.conn = pymysql.connect(SERVER, USER, PASSWORD, DBNAME, charset = 'utf8mb4')
        self.cur = self.conn.cursor()

        self.cur.execute(ANIME_LIST_QUERY)
        rows = self.cur.fetchall()

        self.conn.close()

        return rows

    def getUser(self):
        """ Returns a list of the users in the site. """

        self.conn = pymysql.connect(SERVER, USER, PASSWORD, DBNAME, charset = 'utf8mb4')
        self.cur = self.conn.cursor()

        self.cur.execute(USER_LIST_QUERY)
        rows = self.cur.fetchall()

        self.conn.close()

        return rows

    def insertEpisode(self, episode):
        """ Does a insert query in the database using transaction. """

        self.conn = pymysql.connect(SERVER, USER, PASSWORD, DBNAME, charset = 'utf8mb4')
        self.conn.begin()

        self.cur = self.conn.cursor()
        args = episode.getAttributeList()
        args.extend([timestamp(), VIEWS])
        print('Essa é a lista de argumentos para inserir no banco: ', args)

        try:
            self.cur.execute(INSERT_QUERY, args)
        except Exception as ex:
            print('A inserção falhou, dando rollback nas mudanças...', ex)
            self.conn.rollback()
        else:
            print('Commitando as mudanças feitas...')
            self.conn.commit()
        finally:
            print('Fechando conexão com o banco de dados...')
            self.conn.close()
    
    def isRepeated(self, episode):
        """
            Does a select query in the episode's table to see if the episode is already registered in the database. 
        """

        self.conn = pymysql.connect(SERVER, USER, PASSWORD, DBNAME, charset = 'utf8mb4')
        self.cur = self.conn.cursor()

        showId = episode.animeId
        number = episode.getAttribute('episodio')

        self.cur.execute(IS_REPEATED_QUERY, (showId, number))
        
        result = self.cur.fetchone()
        self.conn.close()

        return result

    def countEpisodes(self, episode):
        """ Counts the number of registered episodes in the database. """

        self.conn = pymysql.connect(SERVER, USER, PASSWORD, DBNAME, charset = 'utf8mb4')
        self.cur = self.conn.cursor()

        self.cur.execute(SELECT_COUNT_QUERY, episode.animeId)
        result = int(self.cur.fetchone()[0])

        print('Quantidade de episódios dessa obra: ', result)

        self.conn.close()

        return result

    def episodeMaxNumber(self, episode):
        """ Returns the maximum number of episodes that the show have. """

        self.conn = pymysql.connect(SERVER, USER, PASSWORD, DBNAME, charset = 'utf8mb4')
        self.cur = self.conn.cursor()

        self.cur.execute(SELECT_NUM_EPISODES_QUERY, episode.animeId)
        result = int(self.cur.fetchone()[0])
        self.conn.close()

        return result

    def insertAndUpdate(self, episode):
        """ 
        Does an insert and an update query in the show's table using transaction.\n
        The update query is to set the show's status to 'complete' if we are inserting its last episode.

        """

        self.conn = pymysql.connect(SERVER, USER, PASSWORD, DBNAME, charset = 'utf8mb4')

        self.conn.begin()
        self.cur = self.conn.cursor()

        args = episode.getAtributeList()
        args.extend([timestamp(), VIEWS])
        print('Essa é a lista de argumentos para inserior no banco: ', args)

        try:
            self.cur.execute(INSERT_QUERY, args)
            self.cur.execute(UPDATE_QUERY, episode.animeId)
        except Exception as exe:
            print('Um problema foi encontrado, dando rollback nas mudanças...', exe)
            self.conn.rollback()
        else:
            print('Commitando as mudanças...')
            self.conn.commit()
        finally:
            print('Finalizando conexão com o banco...')
            self.conn.close()

    def isLast(self, episode):
        """ Verify if the episode is the last episode of the show's season """

        if self.countEpisodes(episode) + 1 == self.episodeMaxNumber(episode):
            return True
        else:
            return False

    def isComplete(self, episode):
        """ Verify if the show is already complete. """

        if self.countEpisodes(episode) == self.episodeMaxNumber(episode):
            return True
        else:
            return False