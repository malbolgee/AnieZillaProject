import json
import bcrypt
import os, sys
from db import *
from tkinter import *
from re import search
from ftplib import FTP
from time import sleep
from threading import Thread
from tkinter import messagebox, filedialog, ttk

PNG = '[.]png\\b'
MP4 = '[.]mp4\\b'
CFG = '[.]cfg\\b'

db = Database()

def resource_path(relative_path):
    
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class App(Tk):

    flag = False

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.container = Frame(self)
        self.container.pack(side = 'top', fill = 'both', expand = True)
        self.container.grid_rowconfigure(0, weight = 1)
        self.container.grid_columnconfigure(0, weight = 1)

        self.footFrame = Frame(self, width = 40, height = 30, bd = 1, relief = GROOVE)
        self.footFrame.pack(side = 'bottom', fill = 'both')

        Label(self.footFrame, text = 'AnieZilla Alpha v0.01', font = ('Calibri', 8, 'italic')).pack(side = LEFT)

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

        if frame.name == 'AnieZilla - Upload' and App.flag == False:
            self.frames[context].fillListBoxupload()
            App.flag = True

        self.title(frame.name)
        frame.tkraise()

        if frame.name != 'AnieZilla - Login':
            menubar = frame.menubar(self)
            self.configure(menu = menubar)

    def loadPages(self, page, container, width, height):

        self.geometry('{}x{}'.format(width, height))
        x = int(self.winfo_screenwidth() / 2 - width / 2)
        y = int(self.winfo_screenheight() / 3 - height / 2)
        self.geometry('+{}+{}'.format(x, y))
        self.minsize(width, height)

        self.show_frame(page)

    def isQuit(self):

        if messagebox.askokcancel('Sair', 'Quer realmente sair?') == True:
            self.quit()

class loginPage(Frame):

    userId = 0
    userVerify = ''
    passwordVerify = ''
    users = db.getUser()

    def __init__(self, parent, controller, name = 'AnieZilla - Login'):

        Frame.__init__(self, parent)
        self.controller = controller

        self.name = name
        self.login = None
        self.label = None
        self.parent = parent

        loginPage.userVerify = StringVar()
        loginPage.passwordVerify = StringVar()

        img = PhotoImage(file = resource_path('logo4.png'))

        label = Label(self, image = img)
        label.image = img
        label.pack(pady = 5)

        Label(self, text = 'User', font = ('Calibri', 11, 'bold')).pack(pady = 2)
        self.userEntry = ttk.Entry(self, textvariable = loginPage.userVerify, width = 25)
        self.userEntry.pack(pady = 2, padx = 10)
        self.userEntry.focus()

        Label(self, text = 'Password', font = ('Calibri', 11, 'bold',)).pack(pady = 2)
        self.passwordEntry = ttk.Entry(self, textvariable = loginPage.passwordVerify, show = '*', width = 25)
        self.passwordEntry.pack(pady = 2)

        loginButton = ttk.Button(self, text = 'Login', width = 10, command = self.verifyLogin)
        loginButton.pack(pady = 5)

    def verifyLogin(self):

        if loginPage.userVerify.get() == '' or loginPage.passwordVerify.get() == '':
            messagebox.showwarning('Campos não preenchidos', 'Todos os campos precisam ser preenchidos')
            return

        else:

            if self.isUser(loginPage.users) == True and self.isPassword(loginPage.passwordVerify.get(), self.login[2]) == True:
                self.controller.loadPages(searchPage, self.controller.container, 376, 361)
            else:
                self.showLabelInvalidLogin()
                return

    def isUser(self, user):
   
        for i in user:
            if loginPage.userVerify.get() == i[1]:
                self.login = i
                print(i)
                loginPage.userId = i[0]
                return True

        return False        

    def isPassword(self, password, hash):

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

    def __init__(self, parent, controller, name = 'AnieZilla - Search'):
        Frame.__init__(self, parent)

        self.name = name
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
            messagebox.showerror("I'm a joke to you?", 'Selecione algum anime na lista.')
            return

        if messagebox.askokcancel('', 'Tem certeza que deseja selecionar ' + searchPage.selectedItem + '?') == True:
            event()

    def fillAnimeList(self):
        
        animes = db.getAnimeList(loginPage.userId)

        self.animeListBox.delete(0, END)

        if not animes:
            messagebox.showinfo('', 'Você não tem nenhum anime para upar!')
            return

        for i in animes:
            searchPage.animeId[i[1]] = (i[0], i[2])
    
        for i in animes:
            self.animeListBox.insert(END, i[1])

    def selectItem(self, event):

        try:

            index = self.animeListBox.curselection()[0]
            searchPage.selectedItem = self.animeListBox.get(index)
            print(searchPage.selectedItem)
            print(searchPage.animeId[searchPage.selectedItem])

        except IndexError:
            pass
            
    def menubar(self, parent):

        menubar = Menu(parent, tearoff = 0)
        fileMenu = Menu(menubar)
        fileMenu.add_command(label = 'Sair', command = lambda: parent.isQuit())

        registryMenu = Menu(menubar)
        registryMenu.add_command(label = 'Cadastrar nova obra')

        menubar.add_cascade(label = 'Arquivo', menu = fileMenu)
        menubar.add_cascade(label = 'Opções', menu = registryMenu)

        return menubar

class directoryPage(Frame):

    path = ''
    fileList = []
    thumbFiles = []
    configFiles = []

    def __init__(self, parent, controller, name = 'AnieZilla Directory'):
        Frame.__init__(self, parent)
        
        self.name = name
        self.parent = parent
        self.controller = controller

        Label(self, text = 'Episódios no diretório', font = ('Arial', 12, 'bold')).pack(pady = 5)

        self.masterFrame = Frame(self, bd = 1, relief = GROOVE)
        self.masterFrame.pack(pady = 2)

        self.scrollBar = ttk.Scrollbar(self.masterFrame)
        self.scrollBar.pack(side = RIGHT, fill = Y)

        self.fileListBox = Listbox(self.masterFrame, height = 13, width = 45, bd = 0)
        self.fileListBox.pack()

        self.scrollBar.config(command = self.fileListBox.yview)
        self.fileListBox.config(yscrollcommand = self.scrollBar.set)

        self.buttonsFrame = Frame(self, width = 30, height = 10)
        self.buttonsFrame.pack()

        self.buttonDirectory = ttk.Button(self.buttonsFrame, text = 'Abrir Diretório', width = 15, command = lambda: self.openDirectory())
        self.buttonDirectory.pack(side = LEFT, pady = 5, padx = 2)

        self.buttonBeginUpload = ttk.Button(self.buttonsFrame, text = 'Fazer Upload', width = 15, command = lambda: self.uploadButton(lambda: controller.show_frame(uploadPage)))
        self.buttonBeginUpload.pack(pady = 5, padx = 2)

        ttk.Button(self, text = 'Voltar', width = 10, command = lambda: controller.show_frame(searchPage)).pack()

    def uploadButton(self, event):

        if not directoryPage.fileList:
            messagebox.showerror('Lista de episódios vazia', 'Não há nada na lista de episódios.')
            return

        event()

    def openDirectory(self):

        directoryPage.path = filedialog.askdirectory() + os.sep
        path = directoryPage.path

        print(path)

        if (len(path) > 1):

            directoryPage.fileList = self.getFiles(path, MP4)
            directoryPage.configFiles = self.getFiles(path, CFG)
            directoryPage.thumbFiles = self.getFiles(path, PNG)

            print(directoryPage.fileList)
            print(directoryPage.configFiles)
            print(directoryPage.thumbFiles)

            fileSize = len(directoryPage.fileList)
            configSize = len(directoryPage.configFiles)
            thumbSize = len(directoryPage.thumbFiles)

            if not directoryPage.fileList:
                self.fileListBox.delete(0, END)
                messagebox.showwarning('', 'Não há arquivos .mp4 no diretório.')
                return

            if not directoryPage.configFiles:
                self.fileListBox.delete(0, END)
                messagebox.showwarning('', 'Não há arquivos .cfg no diretório.')
                return
                
            if not directoryPage.thumbFiles:
                self.fileListBox.delete(0, END)
                messagebox.showwarning('', 'Não há arquivos de thumb no diretório.')
                return

            if fileSize > configSize:
                self.fileListBox.delete(0, END)
                messagebox.showwarning('', 'Um ou mais arquivos .cfg estão faltando.')
                return
            elif fileSize < configSize:
                self.fileListBox.delete(0, END)
                messagebox.showwarning('', 'Um ou mais arquivos .mp4 estão faltando.')
                return
            elif thumbSize < fileSize:
                self.fileListBox.delete(0, END)
                messagebox.showwarning('', 'Uma ou mais thumbs estão faltando.')
                return
     
            self.fillFileList(directoryPage.fileList)

        else:
            print('no directory selected')

    def getFiles(self, path, pattern):

        return [i for i in os.listdir(path) if search(pattern, i)]

    def fillFileList(self, lst):

        self.fileListBox.delete(0, END)
        self.fileListBox.insert(END, *lst)

    def menubar(self, parent):

        menubar = Menu(parent, tearoff = 0)
        fileMenu = Menu(menubar)
        fileMenu.add_command(label = 'Abrir Diretório', command = lambda: self.openDirectory())
        fileMenu.add_separator()
        fileMenu.add_command(label = 'Sair', command = lambda: self.controller.isQuit())

        menubar.add_cascade(label = 'Arquivo', menu = fileMenu)

        return menubar

class uploadPage(Frame):

    flag = True
    
    def __init__(self, parent, controller, name = 'AnieZilla - Upload'):
        Frame.__init__(self, parent)

        self.name = name
        self.parent = parent
        self.tracker = None
        self.controller = controller
        self.fileList = []
        self.configFiles = []
        self.thumbList = []

        self.masterFrame = Frame(self, bd = 1, relief = GROOVE)
        self.masterFrame.pack(pady = 2)

        self.scrollBar = ttk.Scrollbar(self.masterFrame)
        self.scrollBar.pack(side = RIGHT, fill = Y)

        self.uploadListBox = Listbox(self.masterFrame, height = 13, width = 45, bd = 0)
        self.uploadListBox.pack()

        self.scrollBar.config(command = self.uploadListBox.yview)
        self.uploadListBox.config(yscrollcommand = self.scrollBar.set)

        self.buttonFrame = Frame(self)
        self.buttonFrame.pack()

        self.uploadButton = ttk.Button(self.buttonFrame, text = 'Iniciar upload', width = 15, command = self.startThread)
        self.uploadButton.pack(side = LEFT, padx = 2)

        self.pauseUploadButton = ttk.Button(self.buttonFrame, text = 'Pausar Upload', state = DISABLED, width = 15, command = self.startThread)
        self.pauseUploadButton.pack(padx = 2)

    def startThread(self):

        t1 = Thread(target = self.f)
        t1.setDaemon = True
        t1.start()

    def f(self):

        path = directoryPage.path

        for video, config, thumb in zip(self.fileList, self.configFiles, self.thumbList):
            
            try:

                _videoFile = open(path + video[0], 'rb')
                _configFile = open(path + config, 'r', encoding = 'utf-8')
                _thumbFile = open(path + thumb, 'rb')

            except FileNotFoundError as fnf:
                messagebox.showerror('Erro', fnf)
                return

            animeId = searchPage.animeId[searchPage.selectedItem][0]
            animePath = searchPage.animeId[searchPage.selectedItem][1] + '/'
            episodeJson = json.loads(_configFile.read())
            episode = Episode(loginPage.userId, animeId, animePath, video[0], episodeJson)

            maxbytes = int(os.path.getsize(path + video[0]))
            self.tracker = progressBar(self, self.controller, maxbytes)

            try:

                ftp = FTP('ftp.anieclipse.tk')
                ftp.login('anieclipse3', 'StarBugs#029')

                ftp.storbinary('STOR ' + '/public_html/' + animePath + video[0], _videoFile, 8192, self.tracker.updateProgress)
                ftp.storbinary('STOR ' + '/public_html/' + animePath + 'img/' + thumb, _thumbFile)

                db.insertAnime(episode)
                          
                video[1] = True

            except (ConnectionError, TimeoutError) as ce:
                messagebox.showerror('Erro', ce)
                _videoFile.close()
                _thumbFile.close()
                _configFile.close()
                ftp.quit()
                return

            _videoFile.close()
            _thumbFile.close()
            _configFile.close()

            if self.tracker != None:
                self.tracker.progress.destroy()

            self.updateListBoxUpload()

        messagebox.showinfo('', 'Todos os uploads terminaram!')
        ftp.quit()

        return

    def cancelUpload(self):
        print('Cancel Upload')

    def pauseUpload(self):
        print('Pause Upload')

    def helpWindow(self, parent):
        
        win = Toplevel(parent)
        win.geometry('250x250')
        win.resizable(0, 0)
        win.title('Página de Ajuda AnieZilla')
        Label(win, text = 'Teste').pack()

    def updateListBoxUpload(self):
        
        self.uploadListBox.delete(0, END)
        for i in self.fileList:
            if i[1] == True:
                self.uploadListBox.insert(END, i[0] + ' ...Terminado.')
            else:
                self.uploadListBox.insert(END, i[0])

    def fillListBoxupload(self):
        
        for i, j, k in zip(directoryPage.fileList, directoryPage.configFiles, directoryPage.thumbFiles):
            self.fileList.append([i, False])
            self.configFiles.append(j)
            self.thumbList.append(k)

        self.uploadListBox.delete(0, END)
        for i in self.fileList:
            self.uploadListBox.insert(END, i[0])

    def menubar(self, parent):

        menubar = Menu(parent, tearoff = 0)
        fileMenu = Menu(menubar)
        fileMenu.add_command(label = 'Sair', command = lambda: self.controller.isQuit())

        optionsMenu = Menu(menubar)
        optionsMenu.add_command(label = 'Iniciar uploads', state = DISABLED, command = lambda: self.startThread())
        optionsMenu.add_separator()
        optionsMenu.add_command(label = 'Parar todos os uplaods', state = DISABLED, command = lambda: self.cancelUpload())
        optionsMenu.add_command(label = 'Pausar todos os uploads', state = DISABLED, command = lambda: self.pauseUpload())

        helpMenu = Menu(menubar)
        helpMenu.add_command(label = 'Sobre', command = lambda: self.helpWindow(self.controller))

        menubar.add_cascade(label = 'Arquivo', menu = fileMenu)
        menubar.add_cascade(label = 'Opções', menu = optionsMenu)
        menubar.add_cascade(label = 'Ajuda', menu = helpMenu)

        return menubar

class Episode(object):

    def __init__(self, userId, animeId, animePath, fileName, args):
        self.userId = userId
        self.animeId = animeId
        self.animePath = animePath
        self.fileName = fileName
        self.args = args

    def getAtribute(self, name):
        return self.args[name]

class progressBar(Frame):

    def __init__(self, parent, controller, maxbytes):
        Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller
        self.sizeWritten = 0
        self.maxbytes = maxbytes
        self.progress = ttk.Progressbar(parent, orient = 'horizontal', length = 202, mode = 'determinate')
        self.progress['value'] = 0
        self.progress['maximum'] = 100
        self.progress.pack(pady = 5)

    def updateProgress(self, block):
        self.sizeWritten += 8192
        percenteComplete = round((self.sizeWritten / self.maxbytes) * 100)
        self.progress['value'] = percenteComplete

def main():

    app = App()
    app.resizable(0, 0)
    app.mainloop()

main()
