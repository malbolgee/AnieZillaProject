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
        
        self.leftFootFrame = Frame(self.footFrame)
        self.leftFootFrame.pack(side = LEFT)

        self.rightFootFrame = Frame(self.footFrame)
        self.rightFootFrame.pack(side = RIGHT)

        self.footLabel = Label(self.leftFootFrame, text = 'v1.0', font = ('Calibri', 8, 'italic'))
        self.footLabel.pack(side = LEFT)

        self.percentageLabel = Label(self.rightFootFrame, text = '', font = ('Calibri', 8, 'italic'))
        self.percentageLabel.pack(side = RIGHT)

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

        img = PhotoImage(file = resource_path('AnieLogo.png'))

        imageLabel = Label(self, image = img)
        imageLabel.image = img
        imageLabel.pack(pady = 5)

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

    def isUser(self, users):
   
        for user in users:
            if loginPage.userVerify.get() == user[1]:
                self.login = user
                loginPage.userId = user[0]
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
            messagebox.showerror("Am I a joke to you?", 'Selecione algum anime na lista.')
            return

        if messagebox.askokcancel('AnieZilla', 'Tem certeza que deseja selecionar ' + searchPage.selectedItem + '?') == True:
            event()

    def fillAnimeList(self):
        
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

        try:

            index = self.animeListBox.curselection()[0]
            searchPage.selectedItem = self.animeListBox.get(index)

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

    def __init__(self, parent, controller, name = 'AnieZilla Directory'):
        Frame.__init__(self, parent)
        
        self.name = name
        self.parent = parent
        self.controller = controller

        Label(self, text = 'Episódios Selecionados', font = ('Calibri', 12, 'italic')).pack(pady = 5)

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

        self.buttonDirectory = ttk.Button(self.buttonsFrame, text = 'Selecionar Episódios', width = 20, command = lambda: self.openDirectory())
        self.buttonDirectory.pack(side = LEFT, pady = 5, padx = 1)

        self.buttonBeginUpload = ttk.Button(self.buttonsFrame, text = 'Fazer Upload', width = 20, command = lambda: self.uploadButton(lambda: controller.show_frame(uploadPage)))
        self.buttonBeginUpload.pack(pady = 5, padx = 1)

        ttk.Button(self, text = 'Voltar', width = 10, command = lambda: controller.show_frame(searchPage)).pack()

    def uploadButton(self, event):

        if not directoryPage.fileList:
            messagebox.showerror('Lista de episódios vazia', 'Não há nada na lista de episódios.')
            return

        event()

    def openDirectory(self):
        
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
                    messagebox.showwarning('AnieZilla', 'Uma ou mais thumbs estão com o nome incorreto no diretório.')
                    directoryPage.fileList = []
                    directoryPage.thumbFiles = []
                    return

                print('Lista de episódios: ', episodeList)
                episodeNumbers = self.getFileNumber(directoryPage.fileList)

                print('Episode Numbers: ', episodeNumbers)
                print('imgFileList ates do filtro: ', imgFileList)

                directoryPage.thumbFiles = [i for i in imgFileList for j in episodeNumbers if re.search('\\bthumb-{}[.]png\\b'.format(j), i)]

                if len(imgFileList) < len(directoryPage.fileList):
                    messagebox.showwarning('Aniezilla', 'Uma um mais thumbs estão faltando')
                    directoryPage.fileList = []
                    directoryPage.thumbFiles = []
                    return

                print('fileList Preenchido na etapa de abrir diretório: ', directoryPage.fileList)
                print('thumbList Preenchido na etapa de abrir diretório: ', directoryPage.thumbFiles)

                self.fillFileList(self.getFileNames(episodeList))

                print('Lista com os episódios selecionados preenchida!.')
            
            else:
                messagebox.showerror('AnieZilla', 'É preciso existir uma pasta img com os arquivos de thumb no diretório dos episódios.')

    def episodeNameVerify(self):

        return all([re.search(r'\bepisodio-\d+[.]mp4\b', i) for i in directoryPage.fileList])

    def thumbNameVerify(self):

        return all([re.search(r'\bthumb-\d+[.]png\b', i) for i in directoryPage.thumbFiles])

    def getFileNames(self, lst):

        names = []
        for name in lst:
            names.append(re.split('/', name)[-1])

        return names

    def getFiles(self, path, pattern):

        return [i for i in os.listdir(path) if search(pattern, i)]

    def fillFileList(self, lst):

        self.fileListBox.delete(0, END)
        self.fileListBox.insert(END, *lst)

    def getFileNumber(self, fileList):

        numbers = set({})
        for number in fileList:

            x = re.findall(r'\d+', number[:-1])

            print('Nome: ', number, 'Número: ', x)

            if x:
                numbers.add(int(''.join(x)))

        return numbers


    def menubar(self, parent):

        menubar = Menu(parent, tearoff = 0)
        fileMenu = Menu(menubar)
        fileMenu.add_command(label = 'Abrir Diretório', command = lambda: self.openDirectory())
        fileMenu.add_separator()
        fileMenu.add_command(label = 'Sair', command = lambda: self.controller.isQuit())

        menubar.add_cascade(label = 'Arquivo', menu = fileMenu)

        return menubar

class uploadPage(Frame):
    
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

        print('path dos episódios: ', path)

        self.uploadButton['text'] = 'Parar upload'
        self.uploadButton['command'] = self.cancelUpload
        
        try:
            _configFile = open(path + 'config.cfg', 'r', encoding = 'utf-8')
        except FileNotFoundError as fnf:
            messagebox.showwarning('AnieZilla', fnf)
            return

        print('abriu o arquivo .cfg com sucesso!.')

        for video, thumb in zip(self.fileList, self.thumbList):

            print('Iterando agora sobre esse vídeo: {} e esta thumb: {}'.format(video, thumb))
            
            try:

                _videoFile = open(path + video[0], 'rb')
                _thumbFile = open(path + 'img\\' + thumb, 'rb')

            except FileNotFoundError as fnf:
                messagebox.showerror('AnieZilla', fnf)
                _configFile.close()
                return

            print('abriu o vídeo e a thumb com sucesso!')

            animeId = searchPage.animeId[searchPage.selectedItem][0]
            animePath = searchPage.animeId[searchPage.selectedItem][1] + '/'

            episodeJson = json.loads(_configFile.readline())
            episode = Episode(loginPage.userId, animeId, animePath, video[0], episodeJson)

            if db.isRepeated(episode.animeId, episode.getAtribute('episodio')):
                video[2] = True
                _videoFile.close()
                _thumbFile.close()
                self.updateListBoxUpload()
                continue

            maxbytes = int(os.path.getsize(path + video[0]))

            print('O tamanho total do arquivo é: ', maxbytes, ' bytes')

            start_time = datetime.now()

            self.tracker = progressBar(self, self.controller, maxbytes, start_time)

            try:

                ftp = FTP('ftp.anieclipse.tk')
                ftp.login('anieclipse3', 'StarBugs#029')

                self.controller.percentageLabel['text'] = '0% - 0 Kbps'

                print('Começando upload do vídeo...')
                print('Path do anime no servidor: ' + '/public_html/' + animePath + video[0])
                ftp.storbinary('STOR ' + '/public_html/' + animePath + video[0], _videoFile, 8192, self.tracker.updateProgress)

                print('Upload do vídeo terminou com sucesso!')
                print('Começando upload da thumb...')
                print('Path da thumb no servidor: ' + '/public_html/' + animePath + 'img/' + thumb)
                ftp.storbinary('STOR ' + '/public_html/' + animePath + 'img/' + thumb, _thumbFile)
                print('Upload da thumb terminou com sucesso!')

                video[1] = True

                print('Tentando inserir o episódio no banco de dados...')
                db.insertAnime(episode)
                print('Inserção terminada com sucesso!')

            except Exception as ce:
                messagebox.showerror('AnieZilla', ce)
                _configFile.close()
                return

            finally:

                _videoFile.close()
                _thumbFile.close()

                if self.tracker != None:
                    self.tracker.progress.destroy()

                ftp.quit()

            self.updateListBoxUpload()

        messagebox.showinfo('AnieZilla', 'Todos os uploads terminaram!')

    def cancelUpload(self):
        pass

    def pauseUpload(self):
        pass

    def helpWindow(self, parent):
        
        win = Toplevel(parent)
        win.geometry('250x250')
        win.resizable(0, 0)
        win.title('Página de Ajuda AnieZilla')
        Label(win, text = 'Teste').pack()

    def updateListBoxUpload(self):
        
        print('Atualizando lista de episódios para upload')

        self.uploadListBox.delete(0, END)
        for i in self.fileList:
            if i[1] == True:
                self.uploadListBox.insert(END, i[0] + ' ...Terminado.')
            elif i[2] == True:
                self.uploadListBox.insert(END, i[0] + ' ...Repetido, não upado.')
            else:
                self.uploadListBox.insert(END, i[0])

    def fillListBoxupload(self):
        

        print('Preenchendo atributo de lista de arquivos para upload...')
        for i, j in zip(directoryPage.fileList, directoryPage.thumbFiles):
            print('Iterando no video: {} e thumb: {}'.format(i, j))
            self.fileList.append([i, False, False])
            self.thumbList.append(j)

        self.uploadListBox.delete(0, END)

        print('Lista de arquivos para upload: ', self.fileList)

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

def main():

    app = App()
    app.resizable(0, 0)
    app.mainloop()

main()
