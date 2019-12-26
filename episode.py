class Episode(object):

    def __init__(self, userId, animeId, animePath, fileName, args):
        self.userId = userId
        self.animeId = animeId
        self.animePath = animePath
        self.fileName = fileName
        self.args = args

    def getAtribute(self, name):
        return self.args[name]

    def __repr__(self):
        return "userid: {}\n animeId: {}\n animePath: {}\n fileName: {}\n".format(self.userId, self.animeId, self.animePath, self.fileName)