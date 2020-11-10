from constants import *
from threading import Thread
import os, re, json, subprocess
class CFGfile(object):

    def __init__(self, path, episodeList):
        
        self.path = path
        self.quality = None
        self.duration = None
        self.episodeNumbers = set()
        self.episodeList = episodeList
        self.episodeInfoList = []
    
    def getEpisodesNumbers(self):

        for number in self.episodeList:
            x = re.findall(r'\d+', number[:-1])
            if x:
                self.episodeNumbers.add(int(''.join(x)))

    def getEpisodeInfo(self, names, season, EPSCONTINUOUS):

        for number, name in enumerate(names, 1):
            
            if number in self.episodeNumbers:

                input_file = self.path + 'episodio-' + str(number) + '.mp4'

                quality, length = self.getLengthAndQuality(input_file)
                                                
                if EPSCONTINUOUS.get():
                    episodeData = {'temporada' : name[0], 'episodio' : number, 'nome' : name[1], 'duracao' : length, 'thumb' : 'thumb-' + str(number) + '.png', 'qualidade' : quality}
                else:
                    episodeData = {'temporada' : season + 1, 'episodio' : number, 'nome' : name, 'duracao' : length, 'thumb' : 'thumb-' + str(number) + '.png', 'qualidade' : quality}
                
                self.episodeInfoList.append(episodeData)

    def getLengthAndQuality(self, fileName):

        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                'format=duration:stream=height', '-sexagesimal',
                                '-of', 'default=nw=1:nk=1', fileName],
                                stdout = subprocess.PIPE,
                                stderr = subprocess.STDOUT, 
                                stdin = subprocess.PIPE, 
                                universal_newlines = True, shell = True)
        
        result = re.split('\n', result.stdout)
        quality = result[0]
        duration = re.split('\.', result[1])[0]
        return quality + 'p', duration[2:] if duration[0] == '0' else '0' + duration

    def getEpisodeInfoList(self):

        return self.episodeInfoList

    def setCfgFile(self, path, jsonList):
        
        with open(path + 'config.cfg', 'w', encoding = 'utf-8') as cfg:

            for info in jsonList:
                cfg.write(json.dumps(info, ensure_ascii = False))
                cfg.write('\n')
    
    def epsodeNameVerify(self):

        return all([re.search(EPISODE_NAME, j) for j in self.episodeList])