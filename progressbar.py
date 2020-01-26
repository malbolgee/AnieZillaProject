from tkinter import Frame, ttk
from datetime import datetime

class progressBar(Frame):

    def __init__(self, parent, controller, maxbytes, start_time, ftp):
        Frame.__init__(self, parent)

        self.ftp = ftp
        self.timeBegin = 0
        self.controller = controller
        self.sizeWritten = 0
        self.start_time = start_time
        self.maxbytes = maxbytes
        self.progress = ttk.Progressbar(parent, orient = 'horizontal', length = 292, mode = 'determinate')
        self.progress['value'] = 0
        self.progress['maximum'] = 100
        self.progress.grid(row = 0, column = 0)

    def updateProgress(self, block):
        self.sizeWritten += 20000
        percenteComplete = round((self.sizeWritten / self.maxbytes) * 100)
        end_time = datetime.now()

        if (end_time - self.timeBegin).total_seconds() > 10:
            self.timeBegin = datetime.now()
            self.ftp.voidcmd('NOOP')

        kbytespersec = (self.sizeWritten / 1024) / (end_time - self.start_time).total_seconds()
        self.controller.percentageLabel['text'] = '{}% - {:.0f} Kbps'.format(percenteComplete, kbytespersec)
        self.progress['value'] = percenteComplete