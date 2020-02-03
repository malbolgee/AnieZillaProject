from db import *
from tkinter import *
from episode import *
from time import sleep
from progressbar import *
import os, sys, json, bcrypt, glob
from re import search, findall
from datetime import datetime
from threading import Thread
from tkinter import messagebox, filedialog, ttk
from ftpModule import ftpUploadModule

db = Database()

DEBUG = True

def resource_path(relative_path):
    
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class App(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.title('AnieZilla')
        self.resizable(0, 0)
        self.geometry('{}x{}'.format(222, 408))
        x = int((self.winfo_screenwidth() / 2) - (222 / 2))
        y = int((self.winfo_screenheight() / 3) - (408 / 2))
        self.geometry('+{}+{}'.format(x, y))

        if DEBUG:
            self.iconbitmap(resource_path(r'assets\AnieZillaIcon.ico'))
        else:
            self.iconbitmap(resource_path(r'AnieZillaIcon.ico'))

        self.container = Frame(self)
        self.container.pack(side = 'top', fill = 'both', expand = True)
        self.container.grid_rowconfigure(0, weight = 1)
        self.container.grid_columnconfigure(0, weight = 1)

        self.footFrame = Frame(self)
        self.footFrame.pack(side = 'bottom', fill = 'both')
        
        self.leftFootFrame = Frame(self.footFrame)
        self.leftFootFrame.pack(side = 'left')

        self.lockerFrame = Frame(self.footFrame)
        self.lockerFrame.pack(side = 'right')

        self.rightFootFrame = Frame(self.footFrame)
        self.rightFootFrame.pack(side = 'right')

        self.centerFootFrame = Frame(self.footFrame,bg = 'red')
        self.centerFootFrame.pack()

        self.etaLabel = Label(self.leftFootFrame, text = '', font = ('Calibri', 7))
        self.etaLabel.pack(side = 'left')

        self.percentageLabel = Label(self.rightFootFrame, text = '', font = ('Calibri', 8, 'italic'))
        self.percentageLabel.pack(side = 'right')

        self.episodeName = Label(self.centerFootFrame, text = '', font = ('Calibri', 8, 'italic'))
        self.episodeName.pack(side = 'left')

        self.frames = {}

        for F in [loginPage, searchPage, directoryPage, uploadPage]:
            
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = 'nsew')

        self.show_frame(loginPage)

    def show_frame(self, context):

        frame = self.frames[context]
        frame.tkraise()

    def changeTitle(self, title):

        self.title('AnieZilla :: {}'.format(title))

    def loadPages(self, page, container, width, height):

        self.geometry('{}x{}'.format(width, height))
        x = int(self.winfo_screenwidth() / 2 - width / 2)
        y = int(self.winfo_screenheight() / 3 - height / 2)
        self.geometry('+{}+{}'.format(x, y))

        self.show_frame(page)

    def quitButtonUpload(self):

        if messagebox.askokcancel('AnieZilla', 'Existem uploads em andamento, tem certeza que deseja fechar o programa?') == True:
            self.quit()

    def quitButton(self):

        self.quit()

class loginPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.login = None
        self.label = None
        self.loggedUser = None
        self.user = StringVar()
        self.password = StringVar()
        self.controller = controller
        self.name = 'AnieZilla - Login'

        if DEBUG:
            img = PhotoImage(file = resource_path(r'assets\AnieLogo.png'))
        else:
            img = PhotoImage(file = resource_path(r'AnieLogo.png'))

        self.imageLabel = Label(self, image = img)
        self.imageLabel.image = img
        self.imageLabel.pack(pady = 5)

        Label(self, text = 'User', font = ('Calibri', 11, 'bold')).pack(pady = 2)
        self.userEntry = ttk.Entry(self, textvariable = self.user, width = 25)
        self.userEntry.bind('<Return>', self.returnEvent)
        self.userEntry.pack(pady = 2, padx = 10)
        self.userEntry.focus()

        Label(self, text = 'Password', font = ('Calibri', 11, 'bold',)).pack(pady = 2)
        self.passwordEntry = ttk.Entry(self, textvariable = self.password, show = '*', width = 25)
        self.passwordEntry.bind('<Return>', self.returnEvent)
        self.passwordEntry.pack(pady = 2)

        self.loginButton = ttk.Button(self, text = 'Login', width = 10, command = self.verifyLogin)
        self.loginButton.bind('<Return>', self.returnEvent)
        self.loginButton.pack(pady = 5)

    def returnEvent(self, e):

        self.verifyLogin()

    def userAuth(self):
        """ Does the auth for user and password. """

        try:
            self.loggedUser = db.getUser(self.user.get())
            if self.loggedUser:
                if self.passwordAuth(self.password.get(), self.loggedUser['senha']) and self.loggedUser['up'] == 1:
                    return True

            return False

        except Exception as error:
            messagebox.showerror('AnieZilla', error)

    def verifyLogin(self):
        """ Handles the login doing the auth for the user. """

        if self.user.get() == '' or self.password.get() == '':
            messagebox.showwarning('AnieZilla', 'Todos os campos precisam ser preenchidos')
            return
        else:

            if self.userAuth():
                self.controller.loadPages(searchPage, self.controller.container, 376, 361)
            else:
                self.showLabelInvalidLogin()
     
    def passwordAuth(self, password, hash):
        """ Verifies if the password entered is valid. """

        if bcrypt.hashpw(password.encode('utf8'), hash.encode('utf8')) == hash.encode('utf8'):
            return True
        
        return False

    def showLabelInvalidLogin(self):

        if self.label != None:
            self.label.destroy()

        self.label = Label(self, INVALID_LOGIN_LABEL_ARGS)
        self.label.pack()

class searchPage(Frame):

    animeId = {}
    selectedItem = ''

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.controller = controller
        self.name = 'AnieZilla - Search'

        self.label = ttk.Label(self, text = 'Lista de obras', font = ('Calibri', 12, 'italic'))
        self.label.pack(pady = 2)

        self.masterFrame = ttk.Frame(self)
        self.masterFrame.pack(pady = 2) 
        
        self.scrollBar = ttk.Scrollbar(self.masterFrame)
        self.scrollBar.pack(side = RIGHT, fill = Y)

        self.animeListBox = Listbox(self.masterFrame, height = 16, width = 45)
        self.animeListBox.pack()

        self.scrollBar.config(command = self.animeListBox.yview)
        self.animeListBox.config(SHOW_LIST_BOX_ARGS)
        self.animeListBox.config(yscrollcommand = self.scrollBar.set)
        self.animeListBox.bind('<<ListboxSelect>>', self.selectItem)
        self.animeListBox.bind('<Double-Button-1>', self.selecButtonControl)
        self.animeListBox.bind('<Escape>', self.animeListBoxEscapeEvent)

        self.buttonFrame = Frame(self)
        self.buttonFrame.pack()

        self.buttonSelect = ttk.Button(self.buttonFrame, text = 'Selecionar', width = 20)
        self.buttonSelect.bind('<Button-1>', self.selecButtonControl)
        self.buttonSelect.pack()

        self.fillAnimeList()

    def animeListBoxEscapeEvent(self, event):
        
        searchPage.selectedItem = ''
        self.animeListBox.selection_clear(ACTIVE)
        
    def selecButtonControl(self, event):

        self.selectItem(event)
        if  searchPage.selectedItem == '':
            messagebox.showerror("Am I a joke to you?", 'Selecione alguma obra na lista.')
            return

        self.controller.changeTitle(searchPage.selectedItem)
        self.controller.show_frame(directoryPage)

    def fillAnimeList(self):
        """ Fills the Listbox of shows available for episode upload. """
        
        animes = db.getAnimeList()
        self.animeListBox.delete(0, END)

        if not animes:
            messagebox.showinfo('AnieZilla', 'Você não tem nenhum anime para upar!')
            return

        for i in animes:
            searchPage.animeId[i[1]] = (i[0], i[2])
    
        for i in animes:
            self.animeListBox.insert(END, i[1])

    def selectItem(self, event):
        """ Returns the selected item in the listbox of show's """

        searchPage.selectedItem = self.animeListBox.get(ACTIVE)

class directoryPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        
        self.path = ''
        self.fileList = []
        self.thumbFiles = []
        self.episodeNumbers = None
        self.controller = controller
        self.name = 'AnieZilla - Directory'

        self.label = Label(self, text = 'Episódios Selecionados', font = ('Calibri', 12, 'italic'))
        self.label.grid(row = 0, column = 5, columnspan = 6)
     
        self.masterFrame = ttk.Frame(self)
        self.fileListBox = Listbox(self.masterFrame, height = 16, width = 45)
        self.verticalScrollBar = Scrollbar(self.masterFrame, orient = 'vertical', command = self.fileListBox.yview)
        self.fileListBox.config(yscrollcommand = self.verticalScrollBar.set)
        self.fileListBox.config(FILE_LIST_BOX_ARGS)
        self.fileListBox.bind('<Escape>', self.fileListBoxEscapeEvent)
    
        self.masterFrame.grid(row = 1, column = 5, columnspan = 6, rowspan = 3)
        self.fileListBox.grid(row = 0, column = 0, sticky = 'nesw')
        self.verticalScrollBar.grid(row = 0, column = 1, sticky = 'ns')

        self.controlButtonsFrame = Frame(self)
        self.controlButtonsFrame.grid(row = 4, column = 5, columnspan = 6, rowspan = 3)

        self.buttonDirectory = ttk.Button(self.controlButtonsFrame, text = 'Selecionar Episódios', width = 22, command = self.openDirectory)
        self.buttonDirectory.grid(row = 0, column = 0)

        self.buttonBeginUpload = ttk.Button(self.controlButtonsFrame, text = 'Fazer Upload', width = 22, command = self.uploadButton)
        self.buttonBeginUpload.grid(row = 0, column = 2)

        if DEBUG:
            self.imgBackButton = PhotoImage(file = resource_path(r'assets\backButton1.png'))
            self.imgPlusButton = PhotoImage(file = resource_path(r'assets\plusButton.png'))
            self.imgMinusButton = PhotoImage(file = resource_path(r'assets\minusButton.png'))
        else:
            self.imgBackButton = PhotoImage(file = resource_path(r'backButton1.png'))
            self.imgPlusButton = PhotoImage(file = resource_path(r'plusButton.png'))
            self.imgMinusButton = PhotoImage(file = resource_path(r'minusButton.png'))

        self.plusMinusButtonsFrame = Frame(self)
        self.plusMinusButtonsFrame.grid(row = 1, column = 20, rowspan = 3, sticky = 'ns')

        self.plusButton = ttk.Button(self.plusMinusButtonsFrame, image = self.imgPlusButton, command = self.plusButtonCommand)
        self.plusButton.image = self.imgPlusButton
        self.plusButton.grid(row = 0, column = 0, pady = 1, padx = 1)

        self.minusButton = ttk.Button(self.plusMinusButtonsFrame, image = self.imgMinusButton, command = self.minusButtonCommand)
        self.minusButton.image = self.imgMinusButton
        self.minusButton.grid(row = 1, column = 0, pady = 1)

        self.backButton = ttk.Button(self, image = self.imgBackButton, command = self.backButtonCommand)
        self.backButton.image = self.imgBackButton
        self.backButton.grid(row = 0, column = 0)

    def backButtonCommand(self):

        self.controller.frames[searchPage].animeListBox.focus_force()
        self.controller.show_frame(searchPage)

    def fileListBoxEscapeEvent(self, event):

        self.fileListBox.selection_clear(ACTIVE)

    def plusButtonCommand(self):
        """ Handles the plus button command event. """
        
        if not self.fileList:
            messagebox.showerror('AnieZilla', 'Ainda não há episódios selecionados.')
            return
        
        fileName = filedialog.askopenfilename(initialdir = self.path, title = 'Selecione os Episódios', filetypes = [('Arquivos .mp4', '*.mp4')])

        if fileName:
            
            selectedPath = '\\'.join(re.split('/', fileName)[:-1]) + os.sep

            if selectedPath != self.path:
                messagebox.showerror('AnieZilla', 'Selecione um episódio no mesmo diretório dos demais.')
                return

            name = self.getSingleFileName(fileName)
            if not re.search(EPISODE_REGEX, name):
                messagebox.showerror('AnieZilla', 'O nome do episódio selecionado não está no padrão.')
                return

            number = self.getSingleFileNumber(fileName, int)
            if self.episodeNumbers & set({number}):
                messagebox.showerror('AnieZilla', 'Esse episódio já está na lista.')
                return

            if os.path.exists(self.path + '\\' + 'img'):
                
                thumbPath = self.path + 'img' + os.sep + 'thumb-' + str(number) + '.png'
                thumb = re.split('\\\\', glob.glob(thumbPath)[0])[-1]

                if thumb:
                    self.episodeNumbers.add(number)
                    self.fileList.append(name)
                    self.thumbFiles.append(thumb)

                    self.fileList.sort(key = len)
                    self.thumbFiles.sort(key = len)

                    self.fillFileList(self.fileList)
                else:
                    messagebox.showerror('AnieZilla', 'Não existe thumb para esse episódio.')
                    return

            else:
                messagebox.showerror('AnieZilla', 'A pasta img com as thumbs não existe no diretório dos episódios.')
                return

    def getSingleFileName(self, fileName):

        return re.split("(\\\\|/)", fileName)[-1]
        
    def getSingleFileNumber(self, fileName, f):

        return f(re.findall(r'\d+', re.split('/', fileName)[-1])[:-1][0])

    def minusButtonCommand(self):

        try:
            idx = self.fileListBox.curselection()[0]
            self.episodeNumbers.remove(int(''.join(re.findall(r'\d+', self.fileList[idx][:-1]))))
            self.fileList.pop(idx)
            self.thumbFiles.pop(idx)
            self.fileListBox.delete(ACTIVE)
        except IndexError:
            pass

    def clearListBox(self):

        self.fileListBox.delete(0, END)
        self.fileList = []
        self.thumbFiles = []

    def uploadButton(self):

        if not self.fileList:
            messagebox.showerror('AnieZilla', 'Adicione algum episódio para upar.')
            return

        try:

            cfg = open(self.path + 'config.cfg', 'r', encoding = 'utf-8')
            
            self.controller.frames[uploadPage].fillFileList()
            result = self.controller.frames[uploadPage].cfgLineCount(cfg)

            if result == LESS_CFG:
                messagebox.showerror('AnieZilla', 'Há mais arquivos selecionados do que informações disponíveis.')
                return
            if not self.episodeNumberVerify(cfg):
                messagebox.showerror('AnieZilla', 'Um ou mais episódios não tem informações no .cfg')
                return

        except FileNotFoundError as fnf:
            messagebox.showerror('AnieZilla', 'Arquivo config.cfg não encontrado.')
            return

        finally:
            cfg.close()

        self.controller.frames[uploadPage].buttonLock.pack(anchor = 'e')
        self.controller.show_frame(uploadPage)
        self.controller.frames[uploadPage].startThread()

    def episodeNumberVerify(self, cfgFile):
        """ Verifies if all selected files have an info line in the .cfg file. """

        result = self.episodeNumbers.difference({json.loads(num)['episodio'] for num in cfgFile})

        return True if not result else False

    def openDirectory(self):
        """ Method handles the file choosing. """
        
        fileNames = filedialog.askopenfilenames(initialdir = os.getcwd(), title = 'Selecione os Episódios', filetypes = [('Arquivos .mp4', '*.mp4')])

        if fileNames:

            self.clearListBox()
            self.path = '\\'.join(re.split('/', fileNames[0])[:-1]) + os.sep

            self.fileList = [re.split('/', name)[-1] for name in fileNames]
            if not self.episodeNameVerify:
                self.clearLists()
                messagebox.showerror('AnieZilla', 'Um ou mais episódios estão com o nome incorreto.')
                return

            if os.path.exists(self.path + 'img'):

                self.episodeNumbers = self.getFileNumber(self.fileList)
                self.thumbFiles = [name for name in self.fileNameIterator(glob.glob(self.path + 'img\*.png')) if re.search(THUMB_REGEX, name)]

                thumbNumbers = self.getFileNumber(self.thumbFiles)

                if not len(thumbNumbers & self.episodeNumbers) == len(self.fileList):
                    self.clearLists()
                    messagebox.showerror('AnieZilla', 'Um ou mais episódios não tem thumb.')
                    return
        
                self.thumbFiles = [name for name in self.thumbFiles if {int(re.findall(r'\d+', name)[0])} & self.episodeNumbers]

                self.fillFileList(self.fileList)
            
            else:
                messagebox.showerror('AnieZilla', 'É preciso existir uma pasta img com os arquivos de thumb no diretório dos episódios.')

    def fileNameIterator(self, fileList):
        """ Stream of names in fileList. """

        for name in fileList:
            yield re.split("(\\\\|/)", name)[-1]

    def clearLists(self):
        self.fileList = []
        self.thumbFiles = []

    @property
    def episodeNameVerify(self):
        """ Method verifies if all the file names are in the pattern. """

        return all([re.search(EPISODE_REGEX, i) for i in self.fileList])

    def fillFileList(self, lst):
        """ Method fills the Listbox with the selected files. """
        
        self.fileListBox.delete(0, END)
        self.fileListBox.insert(END, *lst)

    def getFileNumber(self, fileList):
        """ Method extracts the number in the file name. """

        return {int(''.join(re.findall(r'\d+', number[:-1]))) for number in fileList}

class uploadPage(Frame):
    
    def __init__(self, parent, controller, name = 'AnieZilla - Upload'):
        Frame.__init__(self, parent)
        
        self.ftp = None
        self.path = ''
        self.name = name
        self.tracker = None
        self.fileList = []
        self.thumbList = []
        self.listBoxNames = []
        self.episodeNumbers = set()
        self.configFile = None
        self.controller = controller
        self.cfgSelectedEntries = None

        self.label = Label(self, text = 'Fila de Uploads', font = ('Calibri', 12, 'italic'))
        self.label.grid(row = 0, column = 5, columnspan = 6)

        self.masterFrame = ttk.Frame(self)
        self.uploadListBox = Listbox(self.masterFrame, height = 16, width = 45)
        self.verticalScrollBar = Scrollbar(self.masterFrame, orient = 'vertical', command = self.uploadListBox.yview)
        self.uploadListBox.config(yscrollcommand = self.verticalScrollBar.set)
        self.uploadListBox.config(UPLOAD_LIST_BOX_ARGS)
        self.uploadListBox.bind('<Escape>', self.uploadListBoxEscapeEvent)

        self.masterFrame.grid(row = 1, column = 5, columnspan = 6, rowspan = 3)
        self.uploadListBox.grid(row = 0, column = 0, sticky = 'nesw')
        self.verticalScrollBar.grid(row = 0, column = 1, sticky = 'ns')

        self.controlButtonsFrame = ttk.Frame(self)
        self.controlButtonsFrame.grid(row = 4, column = 5, columnspan = 6, rowspan = 3)

        self.stopUploadButton = ttk.Button(self.controlButtonsFrame, text = 'Parar Upload', width = 23, command = self.cancelUpload)
        self.stopUploadButton.grid(row = 0, column = 0)

        self.pauseUploadButton = ttk.Button(self.controlButtonsFrame, text = 'Pausar upload', width = 23, command = self.pauseUpload)
        self.pauseUploadButton.grid(row = 0, column = 2)

        if DEBUG:
            self.imgUpButton = PhotoImage(file = resource_path(r'assets\upButton.png'))
            self.imgDownButton = PhotoImage(file = resource_path(r'assets\downButton.png'))
            self.imgPlusButton = PhotoImage(file = resource_path(r'assets\plusButton.png'))
            self.imgMinusButton = PhotoImage(file = resource_path(r'assets\minusButton.png'))
            self.imgBackButton = PhotoImage(file = resource_path(r'assets\backButton1.png'))
        else:
            self.imgUpButton = PhotoImage(file = resource_path(r'upButton.png'))
            self.imgDownButton = PhotoImage(file = resource_path(r'downButton.png'))
            self.imgPlusButton = PhotoImage(file = resource_path(r'plusButton.png'))
            self.imgMinusButton = PhotoImage(file = resource_path(r'minusButton.png'))
            self.imgBackButton = PhotoImage(file = resource_path(r'backButton1.png'))

        self.queueButtonsControlFrame = ttk.Frame(self)
        self.queueButtonsControlFrame.grid(row = 1, column = 20, rowspan = 3 , sticky = 'ns')

        self.plusButton = ttk.Button(self.queueButtonsControlFrame, image = self.imgPlusButton, command = self.plusButtonCommand)
        self.plusButton.image = self.imgPlusButton
        self.plusButton.grid(row = 0, column = 0, pady = 1, padx = 1)

        self.minusButton = ttk.Button(self.queueButtonsControlFrame, image = self.imgMinusButton)
        self.minusButton.image = self.imgMinusButton
        self.minusButton.grid(row = 1, column = 0, pady = 1)

        self.upButton = ttk.Button(self.queueButtonsControlFrame, image = self.imgUpButton)
        self.upButton.image = self.imgUpButton
        self.upButton.grid(row = 2, column = 0, pady = 1, padx = 1)

        self.downButton = ttk.Button(self.queueButtonsControlFrame, image = self.imgDownButton)
        self.downButton.image = self.imgDownButton
        self.downButton.grid(row = 3, column = 0, pady = 1)

        self.progressBarFrame = ttk.Frame(self)
        self.progressBarFrame.grid(row = 8, column = 5, columnspan = 6)

        self.backButton = ttk.Button(self, image = self.imgBackButton, command = self.backButtonCommand)
        self.backButton.image = self.imgBackButton
        self.backButton.grid(row = 0, column = 0)

        if DEBUG:
            self.imgLockerClosed = PhotoImage(file = resource_path(r'assets\padlockClosed.png'))
            self.imgLockerOpen = PhotoImage(file = resource_path(r'assets\padlockOpen.png'))
        else:
            self.imgLockerClosed = PhotoImage(file = resource_path(r'padlockClosed.png'))
            self.imgLockerOpen = PhotoImage(file = resource_path(r'padlockOpen.png'))

        self.buttonLock = Button(controller.lockerFrame, image = self.imgLockerOpen, bd = 0, command = self.lockButtons)
        self.buttonLock.image = self.imgLockerOpen

    def uploadListBoxEscapeEvent(self, event):

        self.uploadListBox.selection_clear(ACTIVE)

    def backButtonCommand(self):
        """ Handles the back button command event. """
        
        self.buttonLock.pack_forget()
        self.controller.show_frame(directoryPage)
        self.uploadListBox.delete(0, END)
        self.controller.episodeName['text'] = ''

    def UnlockButtons(self):
        """ Handles the padlock button event. """
        
        self.upButton['state'] = 'able'
        self.downButton['state'] = 'able'
        self.plusButton['state'] = 'able'
        self.minusButton['state'] = 'able'
        self.buttonLock['image'] = self.imgLockerOpen
        self.buttonLock['command'] = self.lockButtons

        if self.overUpload or self.ftp.stop:
            return

        if self.ftp.pause:
            self.pauseUploadButton['state'] = 'able'
            return

        self.pauseUploadButton['state'] = 'able'
        self.stopUploadButton['state'] = 'able'

    def lockButtons(self):
        """ Handles the padlock button event. """

        self.upButton['state'] = 'disabled'
        self.plusButton['state'] = 'disabled'
        self.minusButton['state'] = 'disabled'
        self.downButton['state'] = 'disabled'
        self.stopUploadButton['state'] = 'disabled'
        self.pauseUploadButton['state'] = 'disabled'
        self.buttonLock['image'] = self.imgLockerClosed
        self.buttonLock['command'] = self.UnlockButtons

    def startThread(self):
        """ Method starts a thread in which the upload module is going to run. """

        t1 = Thread(target = self.f)
        t1.setDaemon = True
        t1.start()

    def f(self):
        
        self.beforeUploadConfig()
        self.path = self.controller.frames[directoryPage].path

        try:

            self.configFile = open(self.path + 'config.cfg', 'r+', encoding = 'utf-8')        

        except FileNotFoundError:
            messagebox.showerror('AnieZilla', 'Arquivo \'config.cfg\' não encontrado.')
            self.controller.protocol('WM_DELETE_WINDOW', self.controller.quitButton)
            self.backButton['state'] = 'normal'
            return

        self.fillListBoxUpload()

        idx = -1
        names = self.listBoxNames
        self.thumbList.sort(key = len)

        for video, thumb, name in zip(self.fileList, self.thumbList, names):
        
            idx += 1
            name[1] = PROCESSING
            self.updateListBoxUpload(idx)
    
            try:

                videoFile = open(self.path + video, 'rb')
                thumbFile = open(self.path + 'img\\' + thumb, 'rb')

            except FileNotFoundError as error:
                messagebox.showerror('AnieZilla', error)

                self.configFile.close()

                self.backButton['state'] = 'normal'
                self.controller.frames[directoryPage].clearListBox()
                self.controller.protocol('WM_DELETE_WINDOW', self.controller.quitButton)

                return
            
            userId = self.controller.frames[loginPage].loggedUser['id']
            animeId = searchPage.animeId[searchPage.selectedItem][0]
            animePath = searchPage.animeId[searchPage.selectedItem][1] + '/'
          
            number = int(re.findall(r'\d+', video)[0])
            episodeJson = self.cfgSelectedEntries[number]
            episode = Episode(userId, animeId, animePath, video, episodeJson)

            try:
                
                if db.isComplete(episode) == True:

                    thumbFile.close()
                    videoFile.close()
                    self.configFile.close()
                    self.backButton['state'] = 'normal'
                    self.controller.protocol('WM_DELETE_WINDOW', self.controller.quitButton)
                    messagebox.showerror('AnieZilla', 'A obra para a qual você está tentando upar o episódio já está completa!')

                    return

            except Exception as error:
                messagebox.showerror('AnieZilla', error)

                self.backButton['state'] = 'normal'
                self.controller.frames[directoryPage].clearListBox()
                self.controller.protocol('WM_DELETE_WINDOW', self.controller.quitButton)

                return

            try:

                if db.isRepeated(episode) != None:
                    name[1] = REPEATED
                    videoFile.close()
                    thumbFile.close()
                    
                    self.eraseUploadedLine(self.configFile, episodeJson)
                    self.updateListBoxUpload(idx)

                    continue

            except Exception as error:
                messagebox.showerror('AnieZilla', error)

                name[1] = ERROR
                thumbFile.close()
                videoFile.close()

                continue

            maxbytes = os.path.getsize(self.path + video)

            try:
                
                self.ftp = ftpUploadModule(FTP_SERVER, FTP_USER, FTP_PASSWORD)

                self.controller.percentageLabel['text'] = '0% - 0 Kbps'
                self.tracker = progressBar(self.progressBarFrame, self.controller, maxbytes, self.ftp)
                self.controller.episodeName['text'] = name[0][:30] + '...' if len(name[0]) > 30 else name[0]

                videoPath = '/public_html/' + animePath + video
                thumbPath = '/public_html/' + animePath + 'img/' + thumb

                rest = None
                fileList = self.ftp.nlst('/public_html/' + animePath)

                if video in fileList:
                    
                    rest = self.ftp.size(videoPath)
                    videoFile.seek(rest, 0)

                    self.tracker.rest = True
                    self.tracker.sizeWrittenRest = rest

                while name[1] != FINISHED:

                    self.ftp.storbinary('STOR ' + videoPath, videoFile, 24576, self.tracker.updateProgress, rest)
                    self.ftp.storbinary('STOR ' + thumbPath, thumbFile)

                    if self.ftp.pause:

                        name[1] = PAUSED
                        self.tracker.rest = True
                        self.updateListBoxUpload(idx)

                        pauseThread = Thread(target = self.ftp.noopLoop)
                        pauseThread.setDaemon(True)
                        pauseThread.start()

                        while self.ftp.pause:
                            sleep(0.3)

                        rest = self.ftp.size(videoPath)
                        videoFile.seek(rest, 0)

                        name[1] = PROCESSING
                        self.tracker.NewSizeWriten = 0
                        self.tracker.sizeWrittenRest = rest
                        self.tracker.start_time = datetime.now()
                        self.updateListBoxUpload(idx)

                    elif self.ftp.stop:
                        break
                    else:
                        name[1] = FINISHED

                if self.ftp.stop:
                    name[1] = STOPED
                    break

                # if not db.isRepeated(episode):
                #     if db.isLast(episode) == False:
                #         db.insertEpisode(episode)
                #     else:
                #         db.insertAndUpdate(episode)
        
                self.eraseUploadedLine(self.configFile, episodeJson)

            except Exception as error:
                messagebox.showerror('AnieZilla', error)

                self.configFile.close()

                name[1] = ERROR
                self.backButton['state'] = 'normal'
                self.updateListBoxUpload(idx)
                self.controller.frames[directoryPage].clearListBox()
                self.controller.protocol('WM_DELETE_WINDOW', self.controller.quitButton)

                return

            finally:

                videoFile.close()
                thumbFile.close()

                if self.tracker != None:
                    self.tracker.progress.destroy()

                self.ftp.quit()

            self.updateListBoxUpload(idx)

        if self.cfgLineCount(self.configFile) == EMPTY_CFG:
            self.configFile.close()
            os.remove(self.path + 'config.cfg')
        else:
            self.configFile.close()

        if not self.ftp.stop:
            messagebox.showinfo('AnieZilla', 'Todos os uploads terminaram!')

        self.updateListBoxUpload(idx)
        self.afterUploadConfig()
    
    def beforeUploadConfig(self):

        self.backButton['state'] = 'disabled'
        self.stopUploadButton['state'] = 'able'
        self.pauseUploadButton['state'] = 'able'
        self.controller.protocol('WM_DELETE_WINDOW', self.controller.quitButtonUpload)
        self.episodeNumbers = self.controller.frames[directoryPage].episodeNumbers

    def afterUploadConfig(self):

        self.backButton['state'] = 'normal'
        self.controller.etaLabel['text'] = ''
        self.stopUploadButton['state'] = 'disabled'
        self.controller.percentageLabel['text'] = ''
        self.pauseUploadButton['state'] = 'disabled'
        self.controller.protocol('WM_DELETE_WINDOW', self.controller.quitButton)
        self.controller.frames[directoryPage].clearListBox()

    def eraseUploadedLine(self, cfgFile, entry):
        """ Method erases a line of info in the .cfg file whose episode has already been uploaded and registered in the database. """

        cfgFile.seek(0)
        arqresult = cfgFile.readlines()
        cfgFile.seek(0)

        tmp = str(entry)
        for line in arqresult:
            x = re.sub('"', '\'', line).strip('\n')
            if x != tmp:
                cfgFile.write(line)

        cfgFile.truncate()
        cfgFile.seek(0)

    def cfgLineCount(self, cfgFile):
        """ Method count the number of lines in the .cfg file. """
        
        i = 0
        for _ in cfgFile:
            i += 1
        
        cfgFile.seek(0)

        if i == 0:
            return EMPTY_CFG
        elif i < len(self.fileList):
            return LESS_CFG
       
    def cancelUpload(self):
        """ Handles the stop upload buttonCommand """
        
        if messagebox.askokcancel('AnieZilla', 'Tem certeza que deseja cancelar o upload?'):
            self.ftp.stop = True
            
    def pauseUpload(self):
        """ Handles the pause upload button command. """
        
        self.ftp.pause = True
        self.ftp.noopLoopFlag = True
        self.stopUploadButton['state'] = 'disable'
        self.pauseUploadButton['text'] = 'Resume Upload'
        self.pauseUploadButton['command'] = self.resumeUpload

    def resumeUpload(self):
        """ Handles the resume upload button command. """

        self.ftp.pause = False
        self.ftp.noopLoopFlag = False
        self.stopUploadButton['state'] = 'able'
        self.pauseUploadButton['text'] = 'Pause Upload'
        self.pauseUploadButton['command'] = self.pauseUpload

    def updateListBoxUpload(self, idx):
        """ Method updates the Listbox with progress on the episodes uploads. """

        name = self.listBoxNames[idx]
        self.uploadListBox.delete(idx)
        
        try:
            self.uploadListBox.insert(idx, str(name[2]) + ': ' + name[0] + UPDATE_UPLOAD_LIST_STRING[name[1]])
            self.uploadListBox.itemconfig(idx, foreground = UPDATE_UPLOAD_LIST_COLOR[name[1]])
        except IndexError:
            self.uploadListBox.insert(idx, str(name[2]) + ': ' + name[0])
    
    def fillFileList(self):
        """ Method fills the Listbox with the selected episodes for upload. """

        self.fileList = []
        self.thumbList = []

        fileList = self.controller.frames[directoryPage].fileList
        thumbFiles = self.controller.frames[directoryPage].thumbFiles

        for file, thumb in zip(fileList, thumbFiles):
            self.fileList.append(file)
            self.thumbList.append(thumb)

    def fillListBoxUpload(self):
        """ Fills the uplod list. """

        self.listBoxNames = []

        for line in self.cfgSelectEntry(self.configFile):

            self.listBoxNames.append([line['nome'], QUEUED, line['episodio']])
            self.uploadListBox.insert(END, str(self.listBoxNames[-1][2]) + ': ' + self.listBoxNames[-1][0])

        self.configFile.seek(0)

    def cfgSelectEntry(self, cfgFile):
        """ Selects the right lines from the .cfg file according to the files selected. """
        
        self.cfgSelectedEntries = {}
        episodeNumbers = self.controller.frames[directoryPage].episodeNumbers

        for line in cfgFile:
            
            x = json.loads(line)

            if x['episodio'] in episodeNumbers:
                self.cfgSelectedEntries[x['episodio']] = x
                yield x
      
    def plusButtonCommand(self):

        if self.overUpload:
            messagebox.showerror('AnieZilla', 'Não é possível adicionar mais nada, todos os uploads já terminaram.')
            return

        if not self.hasCfgInfo(self.configFile):
            messagebox.showerror('AnieZilla', 'Não existe informação no arquivo .cfg para esse episódio.')
            return

        fileName = filedialog.askopenfilename(initialdir = self.path, title = 'Selecione os Episódios', filetypes = [('Arquivos .mp4', '*.mp4')])

        if fileName:

            selectedPath = '\\'.join(re.split('/', fileName)[:-1]) + os.sep

            if selectedPath != self.path:
                messabox.showerror('AnieZilla', 'Selecione um arquivo no mesmo diretório dos demais.')
                return

            name = self.controller.frames[directoryPage].getSingleFileName(fileName, '/')
            if not re.search(EPISODE_REGEX, name):
                messagebox.showerror('AnieZilla', 'O nome do arquivo selecionado não está no padrão.')
                return
            
            number = self.controller.frames[directoryPage].getSingleFileNumber(fileName, int)
            if self.episodeNumbers & set({number}):
                messagebox.showerror('AnieZilla', 'Esse episódio já está na lista.')
                return

            if os.path.exists(self.path + '\\' + 'img'):

                thumbPath = self.path + 'img' + os.sep + 'thumb-' + str(number) + '.png'
                thumb = re.split('\\\\', glob.glob(thumbPath)[0])[-1]

                if thumb:
                    self.fileList.append(name)
                    self.thumbList.append(thumb)
                    self.episodeNumbers.add(number)
                    self.addCfgInfoToEntries(number)
                    self.listBoxNames.append(self.listBoxNameEntry(number))
                    self.uploadListBox.insert(END, str(self.listBoxNames[-1][2]) + ': ' + self.listBoxNames[-1][0])

                else:
                    messagebox.showerror('AnieZilla', 'Não existe thumb para esse episódio.')
                    return
            
            else:
                messagebox.showerror('AnieZilla', 'A pasta img com as thumbs não existe no diretório do episódio.')
                return

    def addCfgInfoToEntries(self, episodeNumber):

        for line in self.configFile:

            x = json.loads(line)
            if x['episodio'] == episodeNumber:
                self.cfgSelectedEntries[x['episodio']] = x
                break

        self.configFile.seek(0)

    def listBoxNameEntry(self, episodeNumber):
        
        entry = self.cfgSelectedEntries[episodeNumber]
        return [entry['nome'], QUEUED, entry['episodio']]

    def hasCfgInfo(self, cfgFile):

        function = self.controller.frames[directoryPage].episodeNumberVerify

        result = function(cfgFile)
        cfgFile.seek(0)

        return result

    @property
    def overUpload(self):

        return all([True if i[1] == FINISHED else False for i in self.listBoxNames]) 

def main():

    app = App()
    app.mainloop()

main()
