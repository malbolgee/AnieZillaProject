from tkinter import ttk, messagebox, filedialog, Frame, Tk, Label, StringVar, END, DISABLED, PhotoImage, Listbox, Text, Scrollbar, BooleanVar
from geturlinfo import urllib, GetUrlInfo
from filecfgmanager import CFGfile
import os, sys, re, json
from constants import *

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

DEBUG = False
class App(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.container = Frame(self)

        if DEBUG:
            self.iconbitmap(resource_path(r'assets\anieGrabberIcon.ico'))
        else:
            self.iconbitmap(resource_path(r'anieGrabberIcon.ico'))
            
        self.container.pack(side = 'top', fill = 'both', expand = True)
        self.container.grid_rowconfigure(0, weight = 1)
        self.container.grid_columnconfigure(0, weight = 1)
        self.hscreen = self.winfo_screenheight()
        self.wscreen = self.winfo_screenwidth()

        self.frames = {}

        for F in [mainPage, autoPage, manualPage]:
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = 'nsew')

        self.loadPage(mainPage, 280, 461)

    def loadPage(self, page, width, height):

        self.geometry('{}x{}'.format(width, height))
        x = int(self.winfo_screenwidth() / 2 - width / 2)
        y = int(self.winfo_screenheight() / 3 - height / 2)
        self.geometry('+{}+{}'.format(x, y))
        self.minsize(width, height)

        self.showFrame(page)

    def showFrame(self, context):

        frame = self.frames[context]
        frame.tkraise()
        
class mainPage(Frame):

    def __init__(self, parent, controller, name = 'mainPage'):
        Frame.__init__(self, parent)
        
        self.name = name
        self.controller = controller
        self.masterFrame = ttk.Frame(self, relief = 'groove', width = 310, height = 300)
        self.masterFrame.pack(pady = 50, fill = 'y', expand = True)
        self.buttonsFrame = Frame(self.masterFrame)
        self.buttonsFrame.pack(pady = 50, padx = 10)
        self.titleLabel = Label(self.buttonsFrame, text = 'Escolha a Opção', font = ('Calibri', 10, 'bold'))
        self.titleLabel.pack(pady = 2)
        self.manualButton = ttk.Button(self.buttonsFrame, text = 'Manual', width = 30, state = DISABLED, command = lambda: controller.loadPage(manualPage, 1200, 400))
        self.manualButton.pack(pady = 2, padx = 3)
        self.automaticButton = ttk.Button(self.buttonsFrame, text = 'Automático', width = 30, command = lambda: controller.loadPage(autoPage, 1200, 400))
        self.automaticButton.pack(pady = 2)

class manualPage(Frame):

    def __init__(self, parent, controller, name = 'manualPage'):
        Frame.__init__(self, parent)

class autoPage(Frame):

    def __init__(self, parent, controller, name = 'autoPage'):
        Frame.__init__(self, parent)

        self.animeInfo = None
        self.cfgFileObject = None
        self.directoryPath = ''
        self.fileNames = []
        self.seasonList = None
        self.seasonDict = {}
        self.listSeasonBoxSelected = ''
        self.controller = controller
        self.EPSCONTINUOUS = BooleanVar()

        self.linkLabel = Label(self, text = 'Forneça o link da obra', font = ('Calibri', 10, 'italic'), width = 45)
        self.linkLabel.grid(row = 0, column = 0, columnspan = 2, padx = 1)

        self.masterFrame = ttk.Frame(self)
        self.masterFrame.grid(row = 1, column = 0, columnspan = 2, sticky = 'nesw')

        self.entryTextLink = StringVar()
        self.entryLink = ttk.Entry(self.masterFrame, width = 45, textvariable = self.entryTextLink)
        self.entryLink.grid(row = 0, column = 0, padx = 1, sticky = 'w')

        if DEBUG:
            self.searchLogo = PhotoImage(file = resource_path(r'assets\searchButton.png'))
        else:
            self.searchLogo = PhotoImage(file = resource_path(r'searchButton.png'))

        self.searchButton = ttk.Button(self.masterFrame, image = self.searchLogo, width = 10, command = self.search)
        self.searchButton.image = self.searchLogo
        self.searchButton.grid(row = 0, column = 1, sticky = 'e')

        self.checkButton = ttk.Checkbutton(self.masterFrame, text = 'Contagem contínua de episódios', onvalue = True, offvalue = False, var = self.EPSCONTINUOUS)
        self.checkButton.grid(row = 1, column = 0, sticky = 'w')

        self.labelSeason = Label(self, text = 'Escolha a Temporada', font = ('Calibri', 10, 'italic'), width = 45)
        self.labelSeason.grid(row = 2, column = 0, pady = 1, padx = 1, columnspan = 2)

        self.listSeasonBox = Listbox(self, height = 17, width = 54)
        self.listSeasonBox.grid(row = 3, column = 0, pady = 1, padx = 1, columnspan = 2, rowspan = 3)
        self.listSeasonBox.bind('<<ListboxSelect>>', self.seasonListBoxSelectItem)

        self.openDirectoryButton = ttk.Button(self, text = 'Escolher episódios', width = 20, command = self.fileSearchCommand)
        self.openDirectoryButton.grid(row = 7, column = 0, columnspan = 2, padx = 1, pady = 2)

        self.episodeInfoLabel = Label(self, text = 'Informações dos Episódios', font = ('Calibri', 10, 'italic'), width = 65)
        self.episodeInfoLabel.grid(row = 0, column = 2, columnspan = 4)

        self.textBoxFrame = Frame(self)
        self.episodeInfoTextBox = Text(self.textBoxFrame, width = 105, height = 20, wrap = 'none')
        self.verticalScrollBar = Scrollbar(self.textBoxFrame, orient = 'vertical', command = self.episodeInfoTextBox.yview)
        self.horizontalScrollBar = Scrollbar(self.textBoxFrame, orient = 'horizontal', command = self.episodeInfoTextBox.xview)
        self.episodeInfoTextBox.configure(yscrollcommand = self.verticalScrollBar.set, xscrollcommand = self.horizontalScrollBar.set)

        self.textBoxFrame.grid(row = 1, column = 2, columnspan = 4, rowspan = 6, pady = 2, padx = 1, sticky = 'nesw')
        self.episodeInfoTextBox.grid(row = 0, column = 0, sticky = 'nesw')
        self.verticalScrollBar.grid(row = 0, column = 1, sticky = 'ns')
        self.horizontalScrollBar.grid(row = 1, column = 0, sticky = 'ew')

        self.generateCfgButton = ttk.Button(self, text = 'Gerar CFG', width = 20, state = 'disabled', command = self.generateCfgCommand)
        self.generateCfgButton.grid(row = 7, column = 4, sticky = 'w')

    def generateCfgCommand(self):
        
        editedJasonList = []
        inputList = re.split('\n', self.episodeInfoTextBox.get('1.0', 'end-2c'))
        
        flag = False
        for info1, info2 in zip(inputList, self.cfgFileObject.episodeInfoList):
            
            editJson = json.loads(re.sub('\'', '"', re.sub('"', '', info1)))
            editedJasonList.append(editJson)

            for key in KEYLIST:

                if editJson[key] != info2[key]:
                    flag = True

        if flag == True:
            if messagebox.askokcancel('AnieGrabber', 'Foram feitas modificações, tem certeza que deseja gerar assim mesmo?'):
                self.cfgFileObject.setCfgFile(self.directoryPath, editedJasonList)
        else:
            if messagebox.askokcancel('AnieGrabber', 'Tem certeza que deseja gerar o arquivo cfg?'):
                self.cfgFileObject.setCfgFile(self.directoryPath, self.cfgFileObject.episodeInfoList)

        messagebox.showwarning('AnieGrabber', 'CFG Criado com sucesso!')
        self.resetAll()

    def resetAll(self):

        self.animeInfo = None
        self.cfgFileObject = None
        self.directoryPath = ''
        self.fileNames = []
        self.seasonList = None
        self.seasonDict = {}
        self.listSeasonBoxSelected = ''
        self.resetEpisodeInfoTextBox()
        self.resetSeasonListBox()
        self.entryLink.delete(0, END)
        self.generateCfgButton['state'] = 'disabled'

    def showInfoCommand(self):
        
        if self.fileNames:
            
            self.resetEpisodeInfoTextBox()

            self.cfgFileObject = CFGfile(self.directoryPath, self.fileNames)
            self.cfgFileObject.getEpisodesNumbers()

            season = self.getSeason()

            if self.EPSCONTINUOUS.get():
                names = self.animeInfo.getAnimeNamesContinuous()
            else:
                names = self.animeInfo.getAnimeNames(season)

            try:
                self.cfgFileObject.getEpisodeInfo(names, season, self.EPSCONTINUOUS)
            except Exception as fnf:
                messagebox.showerror('AnieGrabber' , fnf)
                return

            episodeInfoList = self.cfgFileObject.getEpisodeInfoList()
            
            if self.cfgFileObject.epsodeNameVerify():

                if self.episodeInfoTextBox.get('1.0', END) != '':
                    self.episodeInfoTextBox.delete('1.0', END)

                if episodeInfoList:
                    for info in episodeInfoList:
                        self.episodeInfoTextBox.insert(END, str(info) + '\n')
                    self.generateCfgButton['state'] = 'able'
                else:
                    self.episodeInfoTextBox.insert(END, 'Não há episódios para a temporada escolhida\n')
               
            else:
                messagebox.showerror('AnieGrabber', 'Parece que um ou mais arquivos estão com o nome icorreto.')
                self.resetEpisodeInfoTextBox()
                self.resetSeasonListBox()
                self.entryLink.delete(0, END)

            self.fileNames = []

        else:
            messagebox.showwarning('AnieGrabber', 'Não é possível mostrar informações dos arquivos.')
            return
    
    def resetEpisodeInfoTextBox(self):
        self.episodeInfoTextBox.delete('1.0', END)

    def resetSeasonListBox(self):
        self.listSeasonBox.delete(0, END)   

    def fileSearchCommand(self):
        
        fileNames = filedialog.askopenfilenames(initialdir = os.getcwd(), title = 'Selecione os Episódios', filetypes = [('Arquivos .mp4', '*.mp4')])

        if fileNames:

            self.directoryPath = '\\'.join(re.split('/', fileNames[0])[:-1]) + os.sep
           
            for name in fileNames:
                self.fileNames.append(re.split('/', name)[-1])

            self.showInfoCommand()

    def getAnimeInfo(self):

        if re.search(REGEX_URL, self.entryTextLink.get()):
            self.animeInfo = GetUrlInfo(self.entryTextLink.get())
        else:
            raise ValueError('Formato de link inválido')

    def seasonListBoxSelectItem(self, event):

        try:

            index = self.listSeasonBox.curselection()[0]
            self.listSeasonBoxSelected = self.listSeasonBox.get(index)

        except IndexError:
            pass

    def getSeason(self):
        return self.seasonDict[self.listSeasonBoxSelected]

    def search(self):

        if self.entryTextLink.get() == '':
            messagebox.showwarning('AnieGrabber', 'Forneça um link meu parsero!')
            return

        try:
            self.getAnimeInfo()
        except ValueError as ve:
            messagebox.showerror('AnieGrabber - Link inválido', ve)
            return
        except urllib.error.URLError:
            messagebox.showerror('AnieGrabber', 'Não foi possível acessar o link. Verifique sua conexão com a internet.')
            return

        self.seasonList = self.animeInfo.getSeasonName()
        
        if self.seasonList:
            for num, season in enumerate(self.seasonList):
                self.seasonDict[season] = num
        else:
            self.seasonList.append('Temporada 1')
            self.seasonDict['Temporada 1'] = 0

        self.updateSeasonListBox()
        self.listSeasonBoxSelected = self.listSeasonBox.get(0)

    def updateSeasonListBox(self):

        self.listSeasonBox.delete(0, 'end')
        self.listSeasonBox.insert('end', *self.seasonList)

def main():

    app = App()
    app.title('AnieGrabber')
    app.resizable(0, 0)
    app.mainloop()

main()