import bcrypt
import os, sys
from db import *
from tkinter import *
from re import search
from time import sleep
from threading import Thread
from tkinter import messagebox, filedialog, ttk

""" def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path) """

db = Database()

class App(Tk):

    isRunning = True

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        container = Frame(self)
        container.pack(side = 'top', fill = 'both', expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}

        for F in [loginPage, searchPage, directoryPage]:
            
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = 'nsew')

        self.show_frame(loginPage)

    def show_frame(self, context):
        frame = self.frames[context]

        if frame.name == 'AnieZilla - Search':
            self.frames[context].fillAnimeList()

        self.title(frame.name)
        frame.tkraise()

    def isQuit(self):

        if messagebox.askokcancel('Sair', 'Quer realmente sair?'):
            App.isRunning = False
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

        loginPage.userVerify = StringVar()
        loginPage.passwordVerify = StringVar()

        """ img = PhotoImage(file = resource_path('logo4.png'))

        label = Label(self, image = img)
        label.image = img
        label.pack() """

        Label(self, text = 'User', font = ('Calibri', 11, 'bold')).pack(pady = 2)
        Entry(self, textvariable = loginPage.userVerify).pack(pady = 2, padx = 10)

        Label(self, text = 'Password', font = ('Calibri', 11, 'bold')).pack(pady = 2)
        Entry(self, textvariable = loginPage.passwordVerify, show = '*').pack(pady = 2)

        loginButton = Button(self, text = 'Login', font = ('Calibri', 12), command = self.verifyLogin)
        loginButton.pack(pady = 2)

    def verifyLogin(self):

        if loginPage.userVerify.get() == '' or loginPage.passwordVerify.get() == '':
            messagebox.showwarning('Campos não preenchidos', 'Todos os campos precisam ser preenchidos')
            return

        else:

            if self.isUser(loginPage.users) == True and self.isPassword(loginPage.passwordVerify.get(), self.login[2]) == True:
                messagebox.showinfo('É nóis', 'Você está logado!')
            else:
                self.showLabelInvalidLogin()
                return

            self.controller.show_frame(searchPage)

    def isUser(self, user):
        
        for i in range(len(user)):
            if loginPage.userVerify.get() == user[i][1]:
                self.login = user[i]
                loginPage.userId = user[i][0]
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

    selectedItem = ''
    animeId = {}

    def __init__(self, parent, controller, name = 'AnieZilla - Search'):
        Frame.__init__(self, parent)

        self.controller = controller
        searchPage.run(self.verifyEntry)

        self.name = name

        self.label = Label(self, text = 'Sua lista de animes', font = ('Arial', 12, 'bold'))
        self.label.pack(pady = 2)

        self.masterFrame = Frame(self, bd = 1, relief = GROOVE)
        self.masterFrame.pack(pady = 2) 
        
        self.scrollBar = Scrollbar(self.masterFrame)
        self.scrollBar.pack(side = RIGHT, fill = Y)

        self.animeListBox = Listbox(self.masterFrame, height = 8, width = 28, bd = 0)
        self.animeListBox.pack()

        self.scrollBar.config(command = self.animeListBox.yview)
        self.animeListBox.config(yscrollcommand = self.scrollBar.set)
        self.animeListBox.bind('<<ListboxSelect>>', self.selectItem)

        self.animeSearch = StringVar()

        self.buttonFrame = Frame(self)
        self.buttonFrame.pack()

        self.buttonSelect = Button(self.buttonFrame, text = 'Selecionar', state = DISABLED, width = 10, command = lambda: controller.show_frame(directoryPage))
        self.buttonSelect.pack()

        quitButton = Button(self, text = 'Sair', width = 10, command = lambda: controller.isQuit())
        quitButton.pack()

    def verifyEntry(self):

        while App.isRunning == True:

            sleep(0.2)
            if searchPage.selectedItem == '':
                self.buttonSelect['state'] = DISABLED
            else:
                self.buttonSelect['state'] = NORMAL

    def fillAnimeList(self):
        
        animes = db.getAnimeList(loginPage.userId)

        self.animeListBox.delete(0, END)

        for i in animes:
            searchPage.animeId[i[1]] = (i[0], i[2])
    
        for i in animes:
            self.animeListBox.insert(END, i[1])

    def selectItem(self, event):
        index = self.animeListBox.curselection()[0]
        searchPage.selectedItem = self.animeListBox.get(index)
        print(searchPage.selectedItem)
        print(searchPage.animeId[searchPage.selectedItem])

    @staticmethod
    def run(arg):
        t1 = Thread(target = arg)
        t1.setDaemon(True)
        t1.start()

class directoryPage(Frame):

    fileList = []
    configFiles = []

    def __init__(self, parent, controller, name = 'AnieZilla Directory'):
        Frame.__init__(self, parent)

        directoryPage.run(self.enableUpButtonVerify)
        
        self.controller = controller
        self.parent = parent
        self.name = name

        Label(self, text = 'Episódios no diretório', font = ('Arial', 12)).pack()

        self.masterFrame = Frame(self, bd = 1, relief = GROOVE)
        self.masterFrame.pack(pady = 2)

        self.scrollBar = Scrollbar(self.masterFrame)
        self.scrollBar.pack(side = RIGHT, fill = Y)

        self.fileListBox = Listbox(self.masterFrame, height = 8, width = 31, bd = 0)
        self.fileListBox.pack()

        self.scrollBar.config(command = self.fileListBox.yview)
        self.fileListBox.config(yscrollcommand = self.scrollBar.set)

        self.buttonsFrame = Frame(self, bg = 'red', width = 30, height = 10)
        self.buttonsFrame.pack()

        self.buttonDirectory = Button(self.buttonsFrame, text = 'Abrir Diretório', width = 12, command = lambda: self.openDirectory())
        self.buttonDirectory.pack(side = LEFT)

        self.buttonBeginUpload = Button(self.buttonsFrame, text = 'Upar!', width = 12, state = DISABLED, command = lambda: controller.show_frame(uploadPage))
        self.buttonBeginUpload.pack()

        Button(self, text = 'Voltar', width = 10, command = lambda: controller.show_frame(searchPage)).pack()
        Button(self, text = 'Sair', width = 10, command = lambda: controller.isQuit()).pack()

    def openDirectory(self):

        path = filedialog.askdirectory() + os.sep

        directoryPage.fileList = self.mp4Filter(path)
        directoryPage.configFiles = self.getConfigFiles(path)

        if not directoryPage.fileList:
            self.fileListBox.delete(0, END)
            messagebox.showwarning('', 'Não há arquivos .mp4 no diretório.')
            return

        self.showFileList(directoryPage.fileList)

    def getConfigFiles(self, path):

        return [i for i in os.listdir(path) if search('[.]cfg\\b', i)]

    def showFileList(self, lst):

        self.fileListBox.delete(0, END)
        for i in lst:
            self.fileListBox.insert(END, i)

    def mp4Filter(self, path):
        
        return [i for i in os.listdir(path) if search('[.]mp4\\b', i)]

    def enableUpButtonVerify(self):
        while App.isRunning == True:
            sleep(0.2)
            if not directoryPage.fileList:
                self.buttonBeginUpload['state'] = DISABLED
            else:
                self.buttonBeginUpload['state'] = NORMAL

    @staticmethod
    def run(arg):
        t2 = Thread(target = arg)
        t2.setDaemon = True
        t2.start()

class uploadPage(Frame):

    pass

def main():

    app = App()
    app.geometry('376x361')
    app.minsize(376, 361)
    app.resizable(0, 0)
    app.mainloop()

main()


