from tkinter import Frame, ttk
from datetime import datetime

class progressBar(Frame):

    def __init__(self, parent, controller, maxbytes, ftp):
        Frame.__init__(self, parent)

        self.ftp = ftp
        self.rest = False
        self.stop = False
        self.pause = False
        self.NewSizeWritten = 0
        self.sizeWritten = 0
        self.sizeWrittenRest = 0
        self.maxbytes = maxbytes
        self.controller = controller
        self.timeBegin = datetime.now()
        self.start_time = datetime.now()
        self.progress = ttk.Progressbar(parent, orient = 'horizontal', length = 293, mode = 'determinate')
        self.progress['value'] = 0
        self.progress['maximum'] = 100
        self.progress.grid(row = 0, column = 0)

    def updateProgress(self, block):

        self.sizeWritten += 24576
        self.sizeWrittenRest += 24576

        end_time = datetime.now()

        if (end_time - self.timeBegin).total_seconds() > 10:
            self.timeBegin = datetime.now()
            self.ftp.voidcmd('NOOP')
        
        if self.rest == False:
            kbytespersec = (self.sizeWritten / 1024) / (end_time - self.start_time).total_seconds()
            eta = self.getETA(self.maxbytes - self.sizeWritten, kbytespersec)
        else:
            self.NewSizeWritten += 24576
            kbytespersec = (self.NewSizeWritten / 1024) / (end_time - self.start_time).total_seconds()
            eta = self.getETA(self.maxbytes - self.sizeWrittenRest, kbytespersec)

        self.controller.footLabel['text'] = '{}'.format(eta)
        percenteComplete = round((self.sizeWrittenRest / self.maxbytes) * 100)
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