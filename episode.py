
class Episode(object):

    def __init__(self, userId, animeId, animePath, fileName, args):
        self.userId = userId
        self.animeId = animeId
        self.animePath = animePath
        self.fileName = fileName
        self.args = args

    def getAttribute(self, name):
        """ Returns a single atttribunte value. """

        return self.args[name]

    def getAttributeList(self):
        """ Returns a list with all the attributes of the object. """
        return [self.userId, self.animeId, self.args['nome'], self.args['episodio'], self.args['duracao'], self.args['thumb'], self.fileName, self.args['qualidade'], self.args['temporada']]

    def __repr__(self):
        
        return "userid: {}\nanimeId: {}\nanimePath: {}\nfileName: {}\n".format(self.userId, self.animeId, self.animePath, self.fileName)