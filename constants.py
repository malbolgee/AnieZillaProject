from datetime import datetime

SERVER = 'aniedb.mysql.dbaas.com.br'
USER = 'aniedb'
PASSWORD = 'starred1234'
DBNAME = 'aniedb'

FTP_SERVER = 'ftp.anieclipse.tk'
FTP_USER = 'anieclipse3'
FTP_PASSWORD = 'StarBugs#029'

VIEWS = 0

INSERT_QUERY = "INSERT INTO episodios (idUsuario, idObra, nome, numero, duracao, thumb, nomeArquivo, qualidadeMax, temporada, dataPostagem, views) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
UPDATE_QUERY = "UPDATE obras SET status = 'Completo', upado = 1 WHERE id = %s"
SELECT_COUNT_QUERY = "SELECT COUNT(id) FROM episodios WHERE idObra = %s"
SELECT_NUM_EPISODES_QUERY = "SELECT numeroEpisodios FROM obras WHERE id = %s"
IS_REPEATED_QUERY = "SELECT * FROM episodios WHERE idObra = %s and numero = %s"
ANIME_LIST_QUERY = "SELECT id, nome, diretorio FROM obras INNER JOIN animes ON id = idObra WHERE upado = 0"
USER_LIST_QUERY = "SELECT id, senha, up FROM usuarios WHERE BINARY login = %s"

def timestamp():
    """ Returns a timestamp for the current date and time. """

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

""" Constants for the upload process """
FINISHED = 0
REPEATED = 1
ERROR = 2
PROCESSING = 3
STOPED = 4
PAUSED = 5
QUEUED = 6

UPDATE_UPLOAD_LIST_COLOR = ['green', 'purple', 'red', 'orange', '#8b0000', 'blue']
UPDATE_UPLOAD_LIST_STRING = [' -> Terminado.', ' -> Repetido, não upado.', ' -> Erro no upload.', ' -> Upando...', ' -> Parado.', ' -> Pausado']

EMPTY_CFG = 0
LESS_CFG = 1

THUMB_REGEX = r'\bthumb-\d+[.]png\b'
EPISODE_REGEX = r'\bepisodio-\d+[.]mp4\b'

INVALID_LOGIN_LABEL_ARGS = {'text': 'Login inválido', 'fg': 'red', 'font': ('Calibri', 10, 'italic')}
SHOW_LIST_BOX_ARGS = {'font' : ('Calibri Light', 10), 'relief' : 'flat', 'activestyle' : 'none', 'bd' : 0, 'fg' : '#ef3b37', 'selectbackground' : '#333333', 'selectforeground' : '#ef3b37', 'highlightthickness' : 0}
FILE_LIST_BOX_ARGS = {'font' : ('Calibri Light', 9), 'relief' : 'flat', 'activestyle' : 'none', 'bd' : 0, 'fg' : '#ef3b37', 'selectbackground' : '#333333', 'selectforeground' : '#ef3b37', 'highlightthickness' : 0}
UPLOAD_LIST_BOX_ARGS = {'font' : ('Calibri Light', 9), 'relief' : 'flat', 'activestyle' : 'none', 'bd' : 0, 'fg' : '#ef3b37', 'selectbackground' : '#333333', 'selectforeground' : '#ef3b37', 'highlightthickness' : 0}
