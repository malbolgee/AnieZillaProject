from tkinter import Frame, ttk
from datetime import datetime

class progressBar(Frame):

    def __init__(self, parent, controller, maxbytes, start_time, ftp):
        Frame.__init__(self, parent)

        self.ftp = ftp
        self.stop = False
        self.pause = False
        self.rest = False
        self.sizeWrittenRest = 0
        self.timeBegin = 0
        self.controller = controller
        self.sizeWritten = 0
        self.start_time = start_time
        self.maxbytes = maxbytes
        self.progress = ttk.Progressbar(parent, orient = 'horizontal', length = 293, mode = 'determinate')
        self.progress['value'] = 0
        self.progress['maximum'] = 100
        self.progress.grid(row = 0, column = 0)

    def updateProgress(self, block):

        self.sizeWritten += 20000
        self.sizeWrittenRest += 20000

        percenteComplete = round((self.sizeWrittenRest / self.maxbytes) * 100)
        end_time = datetime.now()

        if (end_time - self.timeBegin).total_seconds() > 10:
            self.timeBegin = datetime.now()
            self.ftp.voidcmd('NOOP')

        kbytespersec = (self.sizeWritten / 1024) / (end_time - self.start_time).total_seconds()
        
        if self.rest == False:
            eta = self.getETA(self.maxbytes - self.sizeWritten, kbytespersec)
        else:
            eta = self.getETA(self.maxbytes - self.sizeWrittenRest, kbytespersec)

        self.controller.footLabel['text'] = '{}'.format(eta)
        self.controller.percentageLabel['text'] = '{}% - {:.0f} Kbps'.format(percenteComplete, kbytespersec)
        self.progress['value'] = percenteComplete

    def getETA(self, size, speed):

        eta = size / (speed * 1000)

        h = int(eta / 3600)
        m = int(eta % 3600 / 60)
        s = int(eta % 3600 % 60)
        
        if m <= 9:
            if m == 0:
                m = '00'
            else:
                m = '0' + str(m)

        if s <= 9:
            if s == 0:
                s = '00'
            else:
                s = '0' + str(s)

        eta = str(m) + ':' + str(s)

        if h <= 9:
            if h == 0:
                eta = '00:' + eta
            else:
                eta = '0' + str(h) + ':' + eta
        else:
            eta = str(h) + ':' + eta

        return eta