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

db = Database()

DEBUG = False

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

        self.footFrame = Frame(self, width = 40, height = 32)
        self.footFrame.pack(side = 'bottom', fill = 'both')
        
        self.leftFootFrame = Frame(self.footFrame, width = 10, height = 30)
        self.leftFootFrame.pack(side = 'left')

        self.lockerFrame = Frame(self.footFrame, width = 20, height = 22)
        self.lockerFrame.pack(side = 'right')

        self.rightFootFrame = Frame(self.footFrame)
        self.rightFootFrame.pack(side = 'right')

        self.footLabel = Label(self.leftFootFrame, text = 'v1.1', font = ('Calibri', 8, 'italic'))
        self.footLabel.pack(side = 'left')

        self.percentageLabel = Label(self.rightFootFrame, text = '', font = ('Calibri', 8, 'italic'))
        self.percentageLabel.pack()

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

        if frame.name == 'AnieZilla - Upload':
            self.frames[context].fillListBoxupload()
            App.flag = True

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

        self.label = ttk.Label(self, text = 'Sua lista de animes', font = ('Arial', 12, 'bold'))
        self.label.pack(pady = 2)

        self.masterFrame = Frame(self, bd = 1, relief = GROOVE)
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

    path = ''
    fileList = []
    thumbFiles = []

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        
        self.name = 'AnieZilla - Directory'
        self.parent = parent
        self.controller = controller
        self.episodeNumbers = None

        Label(self, text = 'Episódios Selecionados', font = ('Calibri', 12, 'italic')).pack(pady = 2)

        self.masterFrame = ttk.Frame(self, relief = 'groove')
        self.masterFrame.pack(pady = 2)

        self.scrollBar = ttk.Scrollbar(self.masterFrame)
        self.scrollBar.pack(side = RIGHT, fill = Y)

        self.fileListBox = Listbox(self.masterFrame, height = 13, width = 45, bd = 0)
        self.fileListBox.pack()

        self.scrollBar.config(command = self.fileListBox.yview)
        self.fileListBox.config(yscrollcommand = self.scrollBar.set)

        self.buttonsFrame = Frame(self, width = 30, height = 10)
        self.buttonsFrame.pack()

        self.buttonDirectory = ttk.Button(self.buttonsFrame, text = 'Selecionar Episódios', width = 20, command = lambda: self.openDirectory())
        self.buttonDirectory.pack(side = LEFT, pady = 5, padx = 1)

        self.buttonBeginUpload = ttk.Button(self.buttonsFrame, text = 'Fazer Upload', width = 20, command = lambda: self.uploadButton(lambda: controller.show_frame(uploadPage)))
        self.buttonBeginUpload.pack(pady = 5, padx = 1)

        self.frame = Frame(self)
        self.frame.pack(side = 'bottom', fill = 'x')

        if DEBUG:
            self.imgBackButton = PhotoImage(file = resource_path(r'assets\backButton.png'))
        else:
            self.imgBackButton = PhotoImage(file = resource_path(r'backButton.png'))


        self.backButton = Button(self.frame, image = self.imgBackButton, bd = 0, command = lambda: controller.show_frame(searchPage))
        self.backButton.image = self.imgBackButton
        self.backButton.pack(anchor = 'w')

    def uploadButton(self, event):

        if not directoryPage.fileList:
            messagebox.showerror('AnieZilla', 'Não há nada na lista de episódios.')
            return

        self.controller.frames[uploadPage].buttonLock.pack(anchor = 'e')
        event()

    def openDirectory(self):
        """ Method handles the file choosing. Making all the necessary treatment. """
        
        fileNames = filedialog.askopenfilenames(initialdir = os.getcwd(), title = 'Selecione os Episódios', filetypes = [('Arquivos .mp4', '*.mp4')])

        if fileNames:

            directoryPage.path = '\\'.join(re.split('/', fileNames[0])[:-1]) + os.sep
            path = directoryPage.path
            
            episodeList = []
            directoryPage.fileList = []
            directoryPage.thumbFiles = []

            for name in fileNames:
                episodeList.append(name)
            
            if os.path.exists(path + '\\' + 'img'):
                
                imgFileList = [i for i in os.listdir(path + '\\' + 'img') if os.path.isfile(path + '\\' + 'img\\' + i)]
                
                directoryPage.thumbFiles = imgFileList
                directoryPage.fileList = self.getFileNames(episodeList)

                if not self.episodeNameVerify():
                    messagebox.showwarning('AnieZilla', 'Um ou mais episódios estão com o nome incorreto.')
                    directoryPage.fileList = []
                    directoryPage.thumbFiles = []
                    return
                
                if not self.thumbNameVerify():
                    messagebox.showwarning('AnieZilla', 'Uma ou mais thumbs estão com o nome incorreto.')
                    directoryPage.fileList = []
                    directoryPage.thumbFiles = []
                    return

                self.episodeNumbers = self.getFileNumber(directoryPage.fileList)

                directoryPage.thumbFiles = [i for i in imgFileList for j in self.episodeNumbers if re.search('\\bthumb-{}[.]png\\b'.format(j), i)]

                if len(imgFileList) < len(directoryPage.fileList):
                    messagebox.showwarning('Aniezilla', 'Uma um mais thumbs estão faltando')
                    directoryPage.fileList = []
                    directoryPage.thumbFiles = []
                    return

                self.fillFileList(self.getFileNames(episodeList))
            
            else:
                messagebox.showerror('AnieZilla', 'É preciso existir uma pasta img com os arquivos de thumb no diretório dos episódios.')

    def episodeNameVerify(self):
        """ Method verifies if all the file names are in the pattern. """

        return all([re.search(r'\bepisodio-\d+[.]mp4\b', i) for i in directoryPage.fileList])

    def thumbNameVerify(self):
        """ Method verifies if all the file names are in the pattern. """

        return all([re.search(r'\bthumb-\d+[.]png\b', i) for i in directoryPage.thumbFiles])

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

        numbers = set({})
        for number in fileList:

            x = re.findall(r'\d+', number[:-1])
            if x:
                numbers.add(int(''.join(x)))

        return numbers

class uploadPage(Frame):
    
    def __init__(self, parent, controller, name = 'AnieZilla - Upload'):
        Frame.__init__(self, parent)

        self.name = name
        self.parent = parent
        self.tracker = None
        self.controller = controller
        self.fileList = []
        self.thumbList = []

        self.masterFrame = ttk.Frame(self , relief = GROOVE)
        self.masterFrame.pack(pady = 2)

        self.scrollBar = ttk.Scrollbar(self.masterFrame)
        self.scrollBar.pack(side = RIGHT, fill = Y)

        self.uploadListBox = Listbox(self.masterFrame, height = 13, width = 45, bd = 0)
        self.uploadListBox.pack()

        self.scrollBar.config(command = self.uploadListBox.yview)
        self.uploadListBox.config(yscrollcommand = self.scrollBar.set)

        self.buttonFrame = Frame(self)
        self.buttonFrame.pack()

        self.uploadButton = ttk.Button(self.buttonFrame, text = 'Iniciar upload', width = 20, command = self.startThread)
        self.uploadButton.pack(side = LEFT, padx = 2)

        self.pauseUploadButton = ttk.Button(self.buttonFrame, text = 'Pausar Upload', state = DISABLED, width = 20, command = self.startThread)
        self.pauseUploadButton.pack(padx = 2)

        self.frame = Frame(self)
        self.frame.pack(side = 'bottom', fill = 'x')

        if DEBUG:
            self.imgBackButton = PhotoImage(file = resource_path(r'assets\backButton.png'))
        else:
            self.imgBackButton = PhotoImage(file = resource_path(r'backButton.png'))


        self.backButton = Button(self.frame, image = self.imgBackButton, bd = 0, command = self.backButtonCommand)
        self.backButton.image = self.imgBackButton
        self.backButton.pack(anchor = 'w')

        if DEBUG:
            self.imgLockerClosed = PhotoImage(file = resource_path(r'assets\padlockClosed.png'))
            self.imgLockerOpen = PhotoImage(file = resource_path(r'assets\padlockOpen.png'))
        else:
            self.imgLockerClosed = PhotoImage(file = resource_path(r'padlockClosed.png'))
            self.imgLockerOpen = PhotoImage(file = resource_path(r'padlockOpen.png'))

        self.buttonLock = Button(controller.lockerFrame, image = self.imgLockerOpen, bd = 0, state = 'disabled', command = self.changeImage)
        self.buttonLock.image = self.imgLockerOpen

    def backButtonCommand(self):
        """ Handles the back button command event. """
        
        self.buttonLock.pack_forget()
        self.controller.show_frame(directoryPage)

    def changeImageBack(self):
        """ Handles a command of the locker button when it's closed. """

        self.buttonLock['image'] = self.imgLockerOpen
        self.buttonLock['command'] = self.changeImage

    def changeImage(self):
        """ Handles a coomand of the locker button when it's open. """

        self.buttonLock['image'] = self.imgLockerClosed
        self.buttonLock['command'] = self.changeImageBack

    def startThread(self):
        """ Method starts a thread in which the upload module is going to run. """

        t1 = Thread(target = self.f)
        t1.setDaemon = True
        t1.start()

    def f(self):

        flag = False
        path = directoryPage.path
        
        self.uploadButton['state'] = 'disabled'
        self.backButton['state'] = 'disabled'
        self.uploadButton['state'] = 'disabled'

        if not self.fileList:
            messagebox.showerror('AnieZilla', 'A lista de upload está vazia!')
            self._activateButtons()
            return
        
        try:

            _configFile = open(path + 'config.cfg', 'r+', encoding = 'utf-8')        

        except FileNotFoundError:
            messagebox.showerror('AnieZilla', 'Arquivo config.cfg não encontrado.')
            self._activateButtons()
            return

        result = self.cfgLineCount(_configFile)

        if result == 1:
            messagebox.showerror('AnieZilla', 'Há mais arquivos selecionados do que informações disponíveis.')
            _configFile.close()
            self._activateButtons()
            return
        else:

            if not self.episodeNumberVerify(_configFile):
                messagebox.showerror('AnieZilla', 'Você está tentando upar episódios para os quais não existem informações.')
                _configFile.close()
                self._activateButtons()
                return

            if result == -1:
                
                flag = True
                self.cfgSelectEntry(path, _configFile)
                _tmpConfigFile = open(path + 'config.tmp', 'r+', encoding = 'utf-8')

        self.thumbList.sort(key = len)
        for video, thumb in zip(self.fileList, self.thumbList):
            
            try:

                _videoFile = open(path + video[0], 'rb')
                _thumbFile = open(path + 'img\\' + thumb, 'rb')

            except FileNotFoundError as fnf:
                messagebox.showerror('AnieZilla', fnf)

                if flag == True:
                    _configFile.close()
                    _tmpConfigFile.close()
                    os.remove(path + 'config.tmp')
                else:
                    _configFile.close()

                self._activateButtons()

                return

            animeId = searchPage.animeId[searchPage.selectedItem][0]
            animePath = searchPage.animeId[searchPage.selectedItem][1] + '/'

            if flag == True:
                episodeJson = json.loads(_tmpConfigFile.readline())
            else:
                episodeJson = json.loads(_configFile.readline())

            episode = Episode(loginPage.userId, animeId, animePath, video[0], episodeJson)

            try:
                
                if db.isComplete(episode) == True:
                    messagebox.showwarning('AnieZilla', 'A obra na para a qual você está tentando upar o episódio já está completa!')
                    _thumbFile.close()
                    _videoFile.close()

                    if flag == True:
                        _configFile.close()
                        _tmpConfigFile.close()
                        os.remove(path + 'config.tmp')
                    else:
                        _configFile.close()

                    self._activateButtons()

                    return

            except Exception as exe:
                messagebox.showerror('AnieZilla', exe)
                self.backButton['state'] = 'normal'
                return

            try:

                if db.isRepeated(episode) != None:
                    video[2] = True
                    _videoFile.close()
                    _thumbFile.close()

                    if flag == True:
                        self.eraseUploadedLine(_configFile, episodeJson)
                        self.eraseUploadedLine(_tmpConfigFile, episodeJson)
                    else:
                        self.eraseUploadedLine(_configFile, episodeJson)

                    self.updateListBoxUpload()
                    continue

            except Exception as exe:
                messagebox.showerror('AnieZilla', exe)
                _thumbFile.close()
                _videoFile.close()
                self._activateButtons()

                continue

            maxbytes = int(os.path.getsize(path + video[0]))
            start_time = datetime.now()

            try:
                
                ftp = FTP('ftp.anieclipse.tk', 'anieclipse3', 'StarBugs#029')

                self.tracker = progressBar(self, self.controller, maxbytes, start_time, ftp)
                self.controller.percentageLabel['text'] = '0% - 0 Kbps'

                serverPath = '/public_html/' + animePath + video[0]
                self.tracker.timeBegin = datetime.now()
                ftp.storbinary('STOR ' + serverPath, _videoFile, 20000, self.tracker.updateProgress)
                
                serverPath = '/public_html/' + animePath + 'img/' + thumb
                ftp.storbinary('STOR ' + serverPath, _thumbFile)

                video[1] = True

                if not db.isRepeated(episode):
                    if db.isLast(episode) == True:
                        db.insertAndUpdate(episode)
                    else:
                        db.insertEpisode(episode)

                if flag == True:
                    self.eraseUploadedLine(_configFile, episodeJson)
                    self.eraseUploadedLine(_tmpConfigFile, episodeJson)
                else:
                    self.eraseUploadedLine(_configFile, episodeJson)

            except Exception as ce:
                messagebox.showerror('AnieZilla', ce)
                if flag == True:
                    _configFile.close()
                    _tmpConfigFile.close()
                    os.remove(path + 'config.tmp')
                else:
                    _configFile.close()

                self._activateButtons()

                return

            finally:

                _videoFile.close()
                _thumbFile.close()

                if flag == True and not _tmpConfigFile.closed:
                    self.updateCfgFile(_tmpConfigFile, _configFile)

                if self.tracker != None:
                    self.tracker.progress.destroy()

                ftp.quit()

            self.updateListBoxUpload()

        if self.cfgLineCount(_configFile) == 2:
            _configFile.close()
            os.remove(path + 'config.cfg')
        else:
            _configFile.close()

        if flag == True and not _tmpConfigFile.closed:
            _tmpConfigFile.close()
            os.remove(path + 'config.tmp')

        messagebox.showinfo('AnieZilla', 'Todos os uploads terminaram!')
        self._activateButtons()

    def _activateButtons(self):

        self.backButton['state'] = 'normal'
        self.uploadButton['text'] = 'Iinicar Upload'
        self.uploadButton['state'] = 'able'

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

    def episodeNumberVerify(self, cfgFile):
        """ Method verifies if the numbers of the episodes in the .cfg file info are equal as the selected files. """

        episodeNumbers = self.controller.frames[directoryPage].episodeNumbers

        for line in cfgFile:

            x = json.loads(line)

            if x['episodio'] not in episodeNumbers:
                return False

        cfgFile.seek(0)

        return True

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

    def updateListBoxUpload(self):
        """ Method updates the Listbox of the progress on de episodes uploads. """

        self.uploadListBox.delete(0, END)
        for i in self.fileList:
            if i[1] == True:
                self.uploadListBox.insert(END, i[0] + ' ...Terminado.')
            elif i[2] == True:
                self.uploadListBox.insert(END, i[0] + ' ...Repetido, não upado.')
            else:
                self.uploadListBox.insert(END, i[0])

    def fillListBoxupload(self):
        """ Method fills the Listbox with the selected episodes for upload. """

        self.fileList = []
        self.thumbList = []
        for i, j in zip(directoryPage.fileList, directoryPage.thumbFiles):
            self.fileList.append([i, False, False])
            self.thumbList.append(j)

        self.uploadListBox.delete(0, END)

        for i in self.fileList:
            self.uploadListBox.insert(END, i[0])

def main():

    app = App()
    app.mainloop()

main()
