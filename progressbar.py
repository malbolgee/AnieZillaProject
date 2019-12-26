from tkinter import Frame, ttk
from datetime import datetime

class progressBar(Frame):

    def __init__(self, parent, controller, maxbytes, start_time):
        Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller
        self.sizeWritten = 0
        self.start_time = start_time
        self.maxbytes = maxbytes
        self.progress = ttk.Progressbar(parent, orient = 'horizontal', length = 202, mode = 'determinate')
        self.progress['value'] = 0
        self.progress['maximum'] = 100
        self.progress.pack(pady = 5)

    def updateProgress(self, block):
        self.sizeWritten += 8192
        percenteComplete = round((self.sizeWritten / self.maxbytes) * 100)
        end_time = datetime.now()
        kbytespersec = (self.sizeWritten / 1024) / (end_time - self.start_time).total_seconds()
        self.controller.percentageLabel['text'] = '{}%      -      {:.0f} Kbps'.format(percenteComplete, kbytespersec)
        self.progress['value'] = percenteComplete