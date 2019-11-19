from tkinter import *
from tkinter import messagebox
from db import *
import bcrypt
from time import sleep
from threading import Thread

db = Database()

class App(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        container = Frame(self)
        container.pack(side = 'top', fill = 'both', expand = True)
        container.grid_rowconfigure(0, weight = 300)
        container.grid_columnconfigure(0, weight = 500)

        self.frames = {}

        for F in [loginPage, searchPage]:

            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = 'nsew')

        self.show_frame(loginPage)

    def show_frame(self, context):
        frame = self.frames[context]
        self.title(frame.name)
        frame.tkraise()

class loginPage(Frame):

    userId = 0
    userVerify = ''
    passwordVerify = ''
    users = db.getUser()

    def __init__(self, parent, controller, name = 'Login'):

        Frame.__init__(self, parent)
        self.controller = controller
        self.name = name
        self.login = None
        self.label = Label(self, text = 'Login inválido', fg = 'red')

        loginPage.userVerify = StringVar()
        loginPage.passwordVerify = StringVar()

        Label(self, text = 'User', font = ('Calibri', 11)).pack()
        self.userLoginEntry = Entry(self, textvariable = loginPage.userVerify)
        self.userLoginEntry.pack(padx = 20)
        Label(self, text = '').pack()

        Label(self, text = 'Password', font = ('Calibri', 11)).pack()
        self.passwordLoginEntry = Entry(self, textvariable = loginPage.passwordVerify, show = '*')
        self.passwordLoginEntry.pack()
        Label(self, text = '')

        loginButton = Button(self, text = 'Login', font = ('Calibri', 12), command = self.verifyLogin)
        loginButton.pack()

    def verifyLogin(self):

        if loginPage.userVerify.get() == '' or loginPage.passwordVerify.get() == '':
            messagebox.showwarning('Campos não preenchidos', 'Todos os campos precisam ser preenchidos')
            return

        else:

            if self.isUser(loginPage.users) == True:

                if self.isPassword(loginPage.passwordVerify.get(), self.login[2]) == True:
                    messagebox.showinfo('É nóis', 'Você está logado!')
                else:
                    messagebox.showwarning('Erro de login', 'Algo deu errado, tente novamente.')
            else:
                messagebox.showwarning('Erro de login', 'Algo deu errado, tente novamente.')
                self.label.destroy()
                self.label = Label(self, text = 'Login inválido', fg = 'red')
                self.label.pack()
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

class searchPage(Frame):

    selectedItem = ''

    def __init__(self, parent, controller, name = 'AnieZilla - Search'):

        Frame.__init__(self, parent)
              
        self.name = name

        self.label = Label(self, text = 'Procure por um anime', font = ('Arial', 12, 'bold'))
        self.label.pack()

        self.masterFrame = Frame(self)
        self.masterFrame.pack()
        self.listFrame = Frame(self.masterFrame)
        self.listFrame.pack(side = LEFT)
        self.scrollFrame = Frame(self.masterFrame)
        self.scrollFrame.pack(side = RIGHT)

        self.animeListBox = None
        self.scrollBar = Scrollbar(self.scrollFrame)

        self.animeSearch = StringVar()

        self.searchBoxEntry = Entry(self, textvariable = self.animeSearch, width = 30)
        self.searchBoxEntry.pack(padx = 30, pady = 10)

        self.buttonFrame = Frame(self)
        self.buttonFrame.pack()

        self.buttonSelect = Button(self.buttonFrame, text = 'Selecionar', width = 10)
        searchPage.run(self.verifyEntry)

        self.buttonSearch = Button(self, text = 'Procurar', width = 10, state = DISABLED, command = lambda: self.searchAnime())
        self.buttonSearch.pack()

        quitButton = Button(self, text = 'Sair', width = 10, command = lambda: self.quit())
        quitButton.pack()

    def searchAnime(self):
        self.showList()

    def showList(self):
        if self.animeListBox == None:
            self.label['text'] = 'Selecione um anime na lista'
            self.animeListBox = Listbox(self.listFrame, height = 8, width = 29)
            self.animeListBox.configure(yscrollcommand = self.scrollBar.set)
            self.scrollBar = Scrollbar(self.scrollFrame)
            self.scrollBar.configure(command = self.animeListBox.yview)
            self.animeListBox.pack()
            self.scrollBar.pack(fill = 'both', expand = True)

            self.animeListBox.bind('<<ListboxSelect>>', self.selectItem)

        self.fillAnimeList()

    def verifyEntry(self):

        while True:

            sleep(0.2)
            if self.animeSearch.get() == '':
                self.buttonSearch['state'] = DISABLED
            else:
                self.buttonSearch['state'] = NORMAL

    def fillAnimeList(self):

        animes = db.getAnimeList(loginPage.userId, self.animeSearch.get())
        self.animeListBox.delete(0, END)

        if not animes:
            messagebox.showwarning('', 'Nenhum anime se encaixa na busca.')
            return

        for i in animes:
            self.animeListBox.insert(END, i[1])

    def selectItem(self, event):
        try:
            self.buttonSelect.pack()
        except:
            pass
        
    @staticmethod
    def run(arg):

        t1 = Thread(target = arg)
        t1.setDaemon(True)
        t1.start()

class menuBar(object):

    def __init__(self, parente, controller, name = 'MenuBar'):
        pass

def main():

    app = App()
    app.mainloop()

main()