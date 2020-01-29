from db import *
from tkinter import *
import os, sys, json, bcrypt
from re import search, findall
from ftplib import FTP
from datetime import datetime
from episode import *
from progressbar import *
from threading import Thread
from tkinter import messagebox, filedialog, ttk
import glob
from time import sleep

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

        if DEBUG:
            self.iconbitmap(resource_path(r'assets\AnieZillaIcon.ico'))
        else:
            self.iconbitmap(resource_path(r'AnieZillaIcon.ico'))

        self.protocol('WM_DELETE_WINDOW', self.quitButton)

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

        self.footLabel = Label(self.leftFootFrame, text = '1.1.11', font = ('Calibri', 8, 'italic'))
        self.footLabel.pack(side = 'left')

        self.percentageLabel = Label(self.rightFootFrame, text = '', font = ('Calibri', 8, 'italic'))
        self.percentageLabel.pack(side = 'right')

        self.episodeName = Label(self.centerFootFrame, text = '', font = ('Calibri', 8, 'italic'))
        self.episodeName.pack(anchor = 'e')

        self.frames = {}

        for F in [loginPage, searchPage, directoryPage, uploadPage]:
            
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = 'nsew')

        self.loadPages(loginPage, self.container, 222, 408)

    def show_frame(self, context):

        frame = self.frames[context]

        if frame.name == 'AnieZilla - Search':
            self.frames[context].fillAnimeList()

        frame.tkraise()

    def changeTitle(self, title):

        self.title('AnieZilla :: {}'.format(title))

    def loadPages(self, page, container, width, height):

        self.geometry('{}x{}'.format(width, height))
        x = int(self.winfo_screenwidth() / 2 - width / 2)
        y = int(self.winfo_screenheight() / 3 - height / 2)
        self.geometry('+{}+{}'.format(x, y))
        self.minsize(width, height)

        self.show_frame(page)

    def quitButton(self):

        if messagebox.askokcancel('AnieZilla', 'Quer realmente sair?') == True:
            self.quit()

class loginPage(Frame):

    userId = 0
    userVerify = ''
    passwordVerify = ''
    users = db.getUser()

    def __init__(self, parent, controller):

        Frame.__init__(self, parent)
        self.controller = controller

        self.name = 'AnieZilla - Login'
        self.login = None
        self.label = None
        self.parent = parent

        loginPage.userVerify = StringVar()
        loginPage.passwordVerify = StringVar()

        if DEBUG:
            img = PhotoImage(file = resource_path(r'assets\AnieLogo.png'))
        else:
            img = PhotoImage(file = resource_path(r'AnieLogo.png'))

        imageLabel = Label(self, image = img)
        imageLabel.image = img
        imageLabel.pack(pady = 5)

        Label(self, text = 'User', font = ('Calibri', 11, 'bold')).pack(pady = 2)
        self.userEntry = ttk.Entry(self, textvariable = loginPage.userVerify, width = 25)
        self.userEntry.bind('<Return>', self.returnEvent)
        self.userEntry.pack(pady = 2, padx = 10)
        self.userEntry.focus()

        Label(self, text = 'Password', font = ('Calibri', 11, 'bold',)).pack(pady = 2)
        self.passwordEntry = ttk.Entry(self, textvariable = loginPage.passwordVerify, show = '*', width = 25)
        self.passwordEntry.bind('<Return>', self.returnEvent)
        self.passwordEntry.pack(pady = 2)

        loginButton = ttk.Button(self, text = 'Login', width = 10, command = self.verifyLogin)
        loginButton.bind('<Return>', self.returnEvent)
        loginButton.pack(pady = 5)

    def returnEvent(self, e):

        self.verifyLogin()

    def verifyLogin(self):
        """ Handles the login doing the auth for the user. """

        if loginPage.userVerify.get() == '' or loginPage.passwordVerify.get() == '':
            messagebox.showwarning('AnieZilla', 'Todos os campos precisam ser preenchidos')
            return

        else:

            if self.isUser(loginPage.users) == True and self.isPassword(loginPage.passwordVerify.get(), self.login[2]) == True:
                self.controller.loadPages(searchPage, self.controller.container, 376, 361)
            else:
                self.showLabelInvalidLogin()
                return

    def isUser(self, users):
        """ Verifies if the user entered is valid. """
   
        for user in users:
            if loginPage.userVerify.get() == user[1]:
                self.login = user
                loginPage.userId = user[0]
                return True

        return False        

    def isPassword(self, password, hash):
        """ Verifies if the password entered is valid. """

        if bcrypt.hashpw(password.encode('utf8'), hash.encode('utf8')) == hash.encode('utf8'):
            return True
        
        return False

    def showLabelInvalidLogin(self):

        if self.label != None:
            self.label.destroy()

        self.label = Label(self, text = 'Login inválido', fg = 'red', font = ('Calibri', 10, 'italic'))
        self.label.pack()

class searchPage(Frame):

    animeId = {}
    selectedItem = ''

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.name = 'AnieZilla - Search'
        self.controller = controller

        self.parent = parent

        self.label = ttk.Label(self, text = 'Sua lista de animes', font = ('Calibri', 12, 'italic'))
        self.label.pack(pady = 2)

        self.masterFrame = ttk.Frame(self)
        self.masterFrame.pack(pady = 2) 
        
        self.scrollBar = ttk.Scrollbar(self.masterFrame)
        self.scrollBar.pack(side = RIGHT, fill = Y)

        self.animeListBox = Listbox(self.masterFrame, height = 13, width = 45, bd = 0)
        self.animeListBox.pack()

        self.scrollBar.config(command = self.animeListBox.yview)
        self.animeListBox.config(yscrollcommand = self.scrollBar.set)
        self.animeListBox.bind('<<ListboxSelect>>', self.selectItem)

        self.animeSearch = StringVar()

        self.buttonFrame = Frame(self)
        self.buttonFrame.pack()

        self.buttonSelect = ttk.Button(self.buttonFrame, text = 'Selecionar', width = 20, command = lambda: self.selecButtonControl(lambda: controller.show_frame(directoryPage)))
        self.buttonSelect.pack()
        
    def selecButtonControl(self, event):
        if  searchPage.selectedItem == '':
            messagebox.showerror("Am I a joke to you?", 'Selecione algum anime na lista.')
            return

        self.controller.changeTitle(searchPage.selectedItem)
        event()

    def fillAnimeList(self):
        """ Fills the Listbox of shows available for episode upload. """
        
        animes = db.getAnimeList(loginPage.userId)

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

        try:

            index = self.animeListBox.curselection()[0]
            searchPage.selectedItem = self.animeListBox.get(index)

        except IndexError:
            pass
   
class directoryPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        
        self.name = 'AnieZilla - Directory'
        self.parent = parent
        self.controller = controller
        self.path = ''
        self.fileList = []
        self.thumbFiles = []
        self.episodeNumbers = None

        self.label = Label(self, text = 'Episódios Selecionados', font = ('Calibri', 12, 'italic'))
        self.label.grid(row = 0, column = 5, columnspan = 6)
     
        self.masterFrame = ttk.Frame(self)
        self.fileListBox = Listbox(self.masterFrame, height = 13, width = 45, bd = 0)
        self.verticalScrollBar = Scrollbar(self.masterFrame, orient = 'vertical', command = self.fileListBox.yview)
        self.fileListBox.configure(yscrollcommand = self.verticalScrollBar.set)

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

        self.backButton = ttk.Button(self, image = self.imgBackButton, command = lambda: controller.show_frame(searchPage))
        self.backButton.image = self.imgBackButton
        self.backButton.grid(row = 0, column = 0)

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

            name = self.getSingleFileName(fileName, '/')
            if not re.search(r'\bepisodio-\d+[.]mp4\b', name):
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

    def getSingleFileName(self, fileName, pattern):

        return re.split(pattern, fileName)[-1]
        
    def getSingleFileNumber(self, fileName, f):

        return f(re.findall(r'\d+', re.split('/', fileName)[-1])[:-1][0])

    def minusButtonCommand(self):

        try:
            idx = self.fileListBox.curselection()[0]
            self.episodeNumbers.remove(int(''.join(re.findall(r'\d+', self.fileList[idx][:-1]))))
            self.fileList.pop(idx)
            self.thumbFiles.pop(idx)
            self.fillFileList(self.fileList)
        except IndexError:
            pass

    def clearListBox(self):

        self.fileListBox.delete(0, END)
        self.fileList = []
        self.thumbFiles = []

    def uploadButton(self):

        if not self.fileList:
            messagebox.showerror('AnieZilla', 'Não há nada na lista de episódios.')
            return

        try:

            cfg = open(self.path + 'config.cfg', 'r', encoding = 'utf-8')

            self.controller.frames[uploadPage].fillFileList()
            result = self.controller.frames[uploadPage].cfgLineCount(cfg)

            if result == 1:
                messagebox.showerror('AnieZilla', 'Há mais arquivos selecionados do que informações disponíveis.')
                return

            elif not self.episodeNumberVerify(cfg):

                messagebox.showerror('AnieZilla', 'Você está tentando upar episódios para os quais não existem informações.')

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

            self.path = '\\'.join(re.split('/', fileNames[0])[:-1]) + os.sep
            path = self.path
            
            episodeList = []
            self.fileList = []
            self.thumbFiles = []

            for name in fileNames:
                episodeList.append(name)
            
            if os.path.exists(path + '\\' + 'img'):
                
                imgFileList = [i for i in os.listdir(path + '\\' + 'img') if os.path.isfile(path + '\\' + 'img\\' + i)]
                
                self.thumbFiles = imgFileList
                self.fileList = self.getFileNames(episodeList)

                if not self.episodeNameVerify():
                    messagebox.showwarning('AnieZilla', 'Um ou mais episódios estão com o nome incorreto.')
                    
                    self.fileList = []
                    self.thumbFiles = []

                    return
                
                if not self.thumbNameVerify():
                    messagebox.showwarning('AnieZilla', 'Uma ou mais thumbs estão com o nome incorreto.')
                    
                    self.fileList = []
                    self.thumbFiles = []

                    return

                self.episodeNumbers = self.getFileNumber(self.fileList)

                self.thumbFiles = [i for i in imgFileList for j in self.episodeNumbers if re.search(r'\bthumb-{}[.]png\b'.format(j), i)]

                if len(imgFileList) < len(self.fileList):
                    messagebox.showwarning('Aniezilla', 'Uma um mais thumbs estão faltando.')

                    self.fileList = []
                    self.thumbFiles = []

                    return

                self.fillFileList(self.fileList)
            
            else:
                messagebox.showerror('AnieZilla', 'É preciso existir uma pasta img com os arquivos de thumb no diretório dos episódios.')

    def episodeNameVerify(self):
        """ Method verifies if all the file names are in the pattern. """

        return all([re.search(r'\bepisodio-\d+[.]mp4\b', i) for i in self.fileList])

    def thumbNameVerify(self):
        """ Method verifies if all the file names are in the pattern. """

        return all([re.search(r'\bthumb-\d+[.]png\b', i) for i in self.thumbFiles])

    def getFileNames(self, lst):

        names = []
        for name in lst:
            names.append(re.split('/', name)[-1])

        return names

    def getFiles(self, path, pattern):

        return [i for i in os.listdir(path) if search(pattern, i)]

    def fillFileList(self, lst):
        """ Method fills the Listbox with the selected files. """
        
        self.fileListBox.delete(0, END)
        self.fileListBox.insert(END, *lst)

    def getFileNumber(self, fileList):
        """ Method extracts the episode number in the file name. """

        numbers = set()
        for number in fileList:

            x = re.findall(r'\d+', number[:-1])
            if x:
                numbers.add(int(''.join(x)))

        return numbers

class uploadPage(Frame):
    
    def __init__(self, parent, controller, name = 'AnieZilla - Upload'):
        Frame.__init__(self, parent)

        self.path = ''
        self.name = name
        self.flag = False
        self.parent = parent
        self.tracker = None
        self.controller = controller
        self.fileList = []
        self.thumbList = []
        self.listBoxNames = []
        self.episodeNumbers = set()
        self.configFile = None
        self.tmpConfigFile = None

        self.label = Label(self, text = 'Fila de Uploads', font = ('Calibri', 12, 'italic'))
        self.label.grid(row = 0, column = 5, columnspan = 6)

        self.masterFrame = ttk.Frame(self)
        self.uploadListBox = Listbox(self.masterFrame, height = 13, width = 45, bd = 0)
        self.verticalScrollBar = Scrollbar(self.masterFrame, orient = 'vertical', command = self.uploadListBox.yview)
        self.uploadListBox.configure(yscrollcommand = self.verticalScrollBar.set)

        self.masterFrame.grid(row = 1, column = 5, columnspan = 6, rowspan = 3)
        self.uploadListBox.grid(row = 0, column = 0, sticky = 'nesw')
        self.verticalScrollBar.grid(row = 0, column = 1, sticky = 'ns')

        self.controlButtonsFrame = ttk.Frame(self)
        self.controlButtonsFrame.grid(row = 4, column = 5, columnspan = 6, rowspan = 3)

        self.stopUploadButton = ttk.Button(self.controlButtonsFrame, text = 'Parar Upload', width = 23)
        self.stopUploadButton.grid(row = 0, column = 0)

        self.pauseUploadButton = ttk.Button(self.controlButtonsFrame, text = 'Pausar upload', width = 23)
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

        self.plusButton = ttk.Button(self.queueButtonsControlFrame, image = self.imgPlusButton)
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

    def backButtonCommand(self):
        """ Handles the back button command event. """
        
        self.buttonLock.pack_forget()
        self.controller.show_frame(directoryPage)
        self.uploadListBox.delete(0, END)
        self.controller.episodeName['text'] = ''

    def UnlockButtons(self):
        """ Handles a command of the locker button when it's closed. """

        self.buttonLock['image'] = self.imgLockerOpen
        self.stopUploadButton['state'] = 'able'
        self.pauseUploadButton['state'] = 'able'
        self.plusButton['state'] = 'able'
        self.minusButton['state'] = 'able'
        self.upButton['state'] = 'able'
        self.downButton['state'] = 'able'
        self.buttonLock['command'] = self.lockButtons

    def lockButtons(self):
        """ Handles a coomand of the locker button when it's open. """

        self.buttonLock['image'] = self.imgLockerClosed
        self.stopUploadButton['state'] = 'disabled'
        self.pauseUploadButton['state'] = 'disabled'
        self.plusButton['state'] = 'disabled'
        self.minusButton['state'] = 'disabled'
        self.upButton['state'] = 'disabled'
        self.downButton['state'] = 'disabled'
        self.buttonLock['command'] = self.UnlockButtons

    def startThread(self):
        """ Method starts a thread in which the upload module is going to run. """

        t1 = Thread(target = self.f)
        t1.setDaemon = True
        t1.start()

    def f(self):

        self.flag = False
        self.backButton['state'] = 'disabled'
        self.path = self.controller.frames[directoryPage].path
        self.episodeNumbers = self.controller.frames[directoryPage].episodeNumbers

        try:

            self.configFile = open(self.path + 'config.cfg', 'r+', encoding = 'utf-8')        

        except FileNotFoundError:
            messagebox.showerror('AnieZilla', 'Arquivo config.cfg não encontrado.')
            self.backButton['state'] = 'normal'
            return

        result = self.cfgLineCount(self.configFile)
        
        if result == -1:
            
            self.flag = True
            self.cfgSelectEntry(self.path, self.configFile)
            self.tmpConfigFile = open(self.path + 'config.tmp', 'r+', encoding = 'utf-8')

        if self.flag == True:
            self.fillListBoxUpload(self.tmpConfigFile)
        else:
            self.fillListBoxUpload(self.configFile)

        idx = -1
        names = self.listBoxNames
        self.thumbList.sort(key = len)

        for video, thumb, name in zip(self.fileList, self.thumbList, names):
        
            idx += 1
            name[1] = PROCESSING
            self.updateListBoxUpload(idx)
    
            try:

                _videoFile = open(self.path + video, 'rb')
                _thumbFile = open(self.path + 'img\\' + thumb, 'rb')

            except FileNotFoundError as fnf:
                messagebox.showerror('AnieZilla', fnf)

                if self.flag == True:
                    self.configFile.close()
                    self.tmpConfigFile.close()
                    os.remove(path + 'config.tmp')
                else:
                    self.configFile.close()

                self.backButton['state'] = 'normal'
                self.controller.frames[directoryPage].clearListBox()

                return

            animeId = searchPage.animeId[searchPage.selectedItem][0]
            animePath = searchPage.animeId[searchPage.selectedItem][1] + '/'

            if self.flag == True:
                episodeJson = json.loads(self.tmpConfigFile.readline())
            else:
                episodeJson = json.loads(self.configFile.readline())

            episode = Episode(loginPage.userId, animeId, animePath, video, episodeJson)

            try:
                
                if db.isComplete(episode) == True:
                    messagebox.showwarning('AnieZilla', 'A obra na para a qual você está tentando upar o episódio já está completa!')
                    _thumbFile.close()
                    _videoFile.close()

                    if self.flag == True:
                        self.configFile.close()
                        self.tmpConfigFile.close()
                        os.remove(self.path + 'config.tmp')
                    else:
                        self.configFile.close()

                    self.backButton['state'] = 'normal'

                    return

            except Exception as exe:
                messagebox.showerror('AnieZilla', exe)

                self.backButton['state'] = 'normal'
                self.controller.frames[directoryPage].clearListBox()

                return

            try:

                if db.isRepeated(episode) != None:
                    name[1] = REPEATED
                    _videoFile.close()
                    _thumbFile.close()

                    if self.flag == True:
                        self.eraseUploadedLine(self.configFile, episodeJson)
                        self.eraseUploadedLine(self.tmpConfigFile, episodeJson)
                    else:
                        self.eraseUploadedLine(self.configFile, episodeJson)

                    self.updateListBoxUpload(idx)
                    continue

            except Exception as exe:
                messagebox.showerror('AnieZilla', exe)

                _thumbFile.close()
                _videoFile.close()

                continue

            maxbytes = int(os.path.getsize(self.path + video))
            start_time = datetime.now()

            try:
                
                ftp = FTP('ftp.anieclipse.tk', 'anieclipse3', 'StarBugs#029')

                self.tracker = progressBar(self.progressBarFrame, self.controller, maxbytes, start_time, ftp)
                self.controller.percentageLabel['text'] = '0% - 0 Kbps'
                self.controller.episodeName['text'] = name[0][:30] + '...' if len(name[0]) > 30 else name[0]

                serverPath = '/public_html/' + animePath + video
                self.tracker.timeBegin = datetime.now()
                # ftp.storbinary('STOR ' + serverPath, _videoFile, 20000, self.tracker.updateProgress)
                
                serverPath = '/public_html/' + animePath + 'img/' + thumb
                # ftp.storbinary('STOR ' + serverPath, _thumbFile)
                
                sleep(5)
                name[1] = FINISHED

                # if not db.isRepeated(episode):
                #     if db.isLast(episode) == False:
                #         db.insertEpisode(episode)
                #     else:
                #         db.insertAndUpdate(episode)

                if self.flag == True:
                    self.eraseUploadedLine(self.configFile, episodeJson)
                    self.eraseUploadedLine(self.tmpConfigFile, episodeJson)
                else:
                    self.eraseUploadedLine(self.configFile, episodeJson)

            except Exception as ce:
                messagebox.showerror('AnieZilla', ce)

                if self.flag == True:
                    self.configFile.close()
                    self.tmpConfigFile.close()
                    os.remove(path + 'config.tmp')
                else:
                    self.configFile.close()

                self.backButton['state'] = 'normal'
                self.controller.frames[directoryPage].clearListBox()

                return

            finally:

                _videoFile.close()
                _thumbFile.close()

                if self.flag == True and not self.tmpConfigFile.closed:
                    self.updateCfgFile(self.tmpConfigFile, self.configFile)

                if self.tracker != None:
                    self.tracker.progress.destroy()

                ftp.quit()

            self.updateListBoxUpload(idx)

        if self.cfgLineCount(self.configFile) == 2:
            self.configFile.close()
            os.remove(self.path + 'config.cfg')
        else:
            self.configFile.close()

        if self.flag == True and not self.tmpConfigFile.closed:
            self.tmpConfigFile.close()
            os.remove(self.path + 'config.tmp')

        messagebox.showinfo('AnieZilla', 'Todos os uploads terminaram!')
        self.backButton['state'] = 'normal'
        self.controller.frames[directoryPage].clearListBox()

    def cfgSelectEntry(self, path, cfgFile):
        """ Method chooses the right lines of info in the .cfg file for the episodes selected. """

        episodeNumbers = self.controller.frames[directoryPage].episodeNumbers
        
        with open(path + 'config.tmp', 'w+', encoding = 'utf-8') as tmp:

            for line in cfgFile:

                x = json.loads(line)

                if x['episodio'] in episodeNumbers:
                    tmp.write(json.dumps(x, ensure_ascii = True))
                    tmp.write('\n')

            cfgFile.seek(0)

    def eraseUploadedLine(self, cfgFile, entry):
        """ Method erases a line of info in the .cfg file whose episode has already been uploaded and registered in the database. """
        
        arqresult = cfgFile.readlines()
        cfgFile.seek(0)

        for line in arqresult:
            if line != entry:
                cfgFile.write(line)

        cfgFile.truncate()
        cfgFile.seek(0)

    def updateCfgFile(self, cfgFileTmp, cfgFile):
        """ Method updates the main .cfg file with the changes made in the temporary .cfg file. """
        
        resultcfg = cfgFile.readlines()
        resulttmp = cfgFileTmp.readlines()
        
        cfgFile.seek(0)
        cfgFileTmp.seek(0)

        for line in resultcfg:
            if line not in resulttmp:
                cfgFile.write(line)

        cfgFile.truncate()
        cfgFile.seek(0)

    def cfgLineCount(self, cfgFile):
        """ Method count the number of lines in the .cfg file. """
        
        i = 0
        for _ in cfgFile:
            i += 1

        if i == 0:
            i = 2
        elif i == len(self.fileList):
            i = 0
        elif i < len(self.fileList):
            i = 1
        elif i > len(self.fileList):
            i = -1

        cfgFile.seek(0)

        return i

    def cancelUpload(self):
        ...

    def pauseUpload(self):
        ...

    def updateListBoxUpload(self, idx):
        """ Method updates the Listbox of the progress on de episodes uploads. """

        name = self.listBoxNames[idx]
        self.uploadListBox.delete(idx, idx)
        
        if name[1] == FINISHED:
            self.uploadListBox.insert(idx, str(name[2]) + ': ' + name[0] + '\t\t -> Terminado')
            self.uploadListBox.itemconfig(idx, foreground = 'green')
        elif name[1] == PROCESSING:
            self.uploadListBox.insert(idx, str(name[2]) + ': ' + name[0] + '\t\t -> Upando...')
            self.uploadListBox.itemconfig(idx, foreground = 'orange')
        elif name[1] == REPEATED:
            self.uploadListBox.insert(idx, str(name[2]) + ': ' + name[0] + '\t\t -> Repetido, não upado')
            self.uploadListBox.itemconfig(idx, foreground = 'purple')
        elif name[1] == ERROR:
            self.uploadListBox.insert(idx, str(name[2]) + ': ' + name[0] + '\t\t -> Erro no upload.')
            self.uploadListBox.itemconfig(idx, foreground = 'red')
        else:
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

    def fillListBoxUpload(self, cfgFile):

        self.listBoxNames = []

        for line in cfgFile:

            x = json.loads(line)
            self.listBoxNames.append([x['nome'], QUEUED, x['episodio']])
            self.uploadListBox.insert(END, str(self.listBoxNames[-1][2]) + ': ' + self.listBoxNames[-1][0])

        cfgFile.seek(0)

    def plusButtonCommand(self):

        if self.overUpload():
            messagebox.showerror('AnieZilla', 'Não é possível adicionar episódio, upload já terminou.')
            return

        if self.flag:
            messagebox.showerror('AnieZilla', 'Não existe informação no arquivo .cfg para esse episódio.')
            return

        fileName = filedialog.askopenfilename(initialdir = self.path, title = 'Selecione os Episódios', filetypes = [('Arquivos .mp4', '*.mp4')])

        if fileName:

            selectedPath = '\\'.join(re.split('/', fileName)[:-1]) + os.sep

            if selectedPath != self.path:
                messabox.showerror('AnieZilla', 'Selecione um episódio no mesmo diretório dos demais.')
                return

            name = self.controller.frames[directoryPage].getSingleFileName(fileName, '/')
            if not re.search(r'\bepisodio-\d+[.]mp4\b', name):
                messagebox.showerror('AnieZilla', 'O nome do episódio selecionado não está no padrão.')
                return
            
            number = self.controller.frames[directoryPage].getSingleFileNumber(fileName, int)
            if self.episodeNumbers & set({number}):
                messagebox.showerror('AnieZilla', 'Esse episódio já está na lista.')
                return
            
            if not self.hasCfgInfo(self.configFile):
                messagebox.showerror('AnieZilla', 'Não existe informação no arquivo cfg para esse episódio.')
                return

            if os.path.exists(self.path + '\\' + 'img'):

                thumbPath = self.path + 'img' + os.sep + 'thumb-' + str(number) + 'png'
                thumb = re.split('\\\\', glob.blog(thumbPath)[0])[-1]

                if thumb:
                    self.episodeNumbers.add(number)
                    self.fileList.append([name, QUEUED])
                    self.thumbList.append(thumb)

                    # self.updateListBoxUpload()
                
                else:
                    messagebox.showerror('AnieZilla', 'Não existe thumb para esse episódio.')
                    return
            
            else:
                messagebox.showerror('AnieZilla', 'A pasta img com as thumbs não existe no diretório do episódio.')
                return

    # Verificar função
    def getIdxListBoxSelected(self):

        try:

            idx = self.fillListBoxUpload.curselection()[0]

        except IndexError:
            pass
            
        return idx

    def hasCfgInfo(self, cfgFile):

        function = self.controller.frames[directoryPage].episodeNumberVerify

        result = function(cfgFile)
        cfgFile.seek(0)

        return result

    def overUpload(self):

        return all([True if i[1] == FINISHED else False for i in self.listBoxNames]) 

def main():

    app = App()
    app.mainloop()

main()
