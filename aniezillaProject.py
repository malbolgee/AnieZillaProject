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

        self.footLabel = Label(self.leftFootFrame, text = 'v1.1', font = ('Calibri', 8, 'italic'))
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

        img = PhotoImage(file = resource_path(r'assets\AnieLogo.png'))

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
        """ Handles the login doing the auth for the user. """

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
        self.episodeNumbers = None

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
                    messagebox.showwarning('AnieZilla', 'Uma ou mais thumbs estão com o nome incorreto no diretório.')
                    directoryPage.fileList = []
                    directoryPage.thumbFiles = []
                    return

                print('Lista de episódios: ', episodeList)
                self.episodeNumbers = self.getFileNumber(directoryPage.fileList)

                print('Episode Numbers: ', self.episodeNumbers)
                print('imgFileList ates do filtro: ', imgFileList)

                directoryPage.thumbFiles = [i for i in imgFileList for j in self.episodeNumbers if re.search('\\bthumb-{}[.]png\\b'.format(j), i)]

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
        """ Method starts a thread in which the upload module is going to run. """

        t1 = Thread(target = self.f)
        t1.setDaemon = True
        t1.start()

    def f(self):

        flag = False
        path = directoryPage.path

        print('path dos episódios: ', path)
        
        self.uploadButton['state'] = 'disabled'
        self.uploadButton['text'] = 'Parar Upload'

        try:

            _configFile = open(path + 'config.cfg', 'r+', encoding = 'utf-8')        

        except FileNotFoundError:
            messagebox.showerror('AnieZilla', 'Arquivo config.cfg não encontrado.')
            return

        print('abriu o arquivo .cfg com sucesso!.')
        print('Comparando quantidade de entradas no .cfg com a quantidade de arquivos na fila para upar...')

        result = self.cfgLineCount(_configFile)

        if result == 1:
            messagebox.showerror('AnieZilla', 'Há mais arquivos selecionados do que informações disponíveis.')
            _configFile.close()
            return
        else:

            if not self.episodeNumberVerify(_configFile):
                messagebox.showerror('AnieZilla', 'Você está tentando upar episódios para os quais não existem informações.')
                _configFile.close()
                return

            if result == 0:
                ...
            elif result == -1:
                
                flag = True
                print('A quantidade de infos é maior do que a quantidade de episódios selecionada...')
                self.cfgSelectEntry(path, _configFile)
                print('Selecionando as linhas corretas de informações...')
                _tmpConfigFile = open(path + 'config.tmp', 'r+', encoding = 'utf-8')
                print('Criado arquivo config temporário para lidar com isso...')

        self.thumbList.sort(key = len)
        for video, thumb in zip(self.fileList, self.thumbList):

            print('Iterando agora sobre esse vídeo: {} e esta thumb: {}'.format(video, thumb))
            
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

                return

            print('abriu o vídeo e a thumb com sucesso!')

            animeId = searchPage.animeId[searchPage.selectedItem][0]
            animePath = searchPage.animeId[searchPage.selectedItem][1] + '/'

            if flag == True:
                print('Lendo o arquivo de infos do cfg temporário...')
                episodeJson = json.loads(_tmpConfigFile.readline())
            else:
                print('Lendo o arquivo de infos do cfg principal...')
                episodeJson = json.loads(_configFile.readline())

            print('Criando o objeto episódio...')
            episode = Episode(loginPage.userId, animeId, animePath, video[0], episodeJson)

            print('Consultando no banco por repetição de registro...')
            print('A consulta no banco retornou: ', db.isRepeated(episode))

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

                    return

            except Exception as exe:
                messagebox.showerror('AnieZilla', exe)
                return

            try:

                if db.isRepeated(episode) != None:
                    video[2] = True
                    _videoFile.close()
                    _thumbFile.close()

                    if flag == True:
                        print('Apagando entrada dos cfgs...')
                        self.eraseUploadedLine(_configFile, episodeJson)
                        self.eraseUploadedLine(_tmpConfigFile, episodeJson)
                    else:
                        print('Apagando entrada do cfg principal...')
                        self.eraseUploadedLine(_configFile, episodeJson)

                    self.updateListBoxUpload()
                    print('O episódio já estava cadastrado no banco, indo para o próximo da lista...')
                    continue

            except Exception as exe:
                messagebox.showerror('AnieZilla', exe)
                _thumbFile.close()
                _videoFile.close()
            
                continue

            maxbytes = int(os.path.getsize(path + video[0]))
            print('O tamanho total do arquivo é: ', maxbytes, ' bytes')
            start_time = datetime.now()

            try:
                
                print('Iiniciando conexão ftp...')
                ftp = FTP('ftp.anieclipse.tk', 'anieclipse3', 'StarBugs#029')
                print('Conexão iniciada com sucesso!')

                self.tracker = progressBar(self, self.controller, maxbytes, start_time, ftp)
                self.controller.percentageLabel['text'] = '0% - 0 Kbps'

                print('Começando upload do vídeo...')
                serverPath = '/public_html/' + animePath + video[0]
                print('Path do anime no servidor: ' + serverPath)
                self.tracker.timeBegin = datetime.now()
                print(ftp.storbinary('STOR ' + serverPath, _videoFile, 20000, self.tracker.updateProgress))
                print('Upload do vídeo terminou com sucesso!')

                serverPath = '/public_html/' + animePath + 'img/' + thumb
                print('Começando upload da thumb...')
                print('Path da thumb no servidor: ', serverPath)
                print(ftp.storbinary('STOR ' + serverPath, _thumbFile))
                print('Upload da thumb terminou com sucesso!')

                video[1] = True

                if db.isLast(episode) == True:
                    print('Esse episódio é o último dessa obra, fazendo transaction (update e inserção)')
                    db.insertAndUpdate(episode)
                    print('Transaction completada com sucesso!')
                    messagebox.showinfo('AnieZilla', 'O ùltimo episódio dessa obra foi upado!')

                    if flag == True:
                        print('Atualzando os .cfg...')
                        self.eraseUploadedLine(_configFile, episodeJson)
                        self.eraseUploadedLine(_tmpConfigFile, episodeJson)
                    else:
                        print('Atualizando o .cfg principal...')
                        self.eraseUploadedLine(_configFile, episodeJson)
                    
                else:
                    print('Esse episódio não é o último dessa obra, inserindo normalmente (apenas inserção)')
                    db.insertEpisode(episode)
                    print('Inserção terminada com sucesso!')

                    if flag == True:
                        print('Atualizando os .cfg...')
                        self.eraseUploadedLine(_configFile, episodeJson)
                        self.eraseUploadedLine(_tmpConfigFile, episodeJson)
                    else:
                        print('Atualizando o .cfg principal...')
                        self.eraseUploadedLine(_configFile, episodeJson)

                print('Atualização realizada com sucesso!')

            except Exception as ce:
                messagebox.showerror('AnieZilla', ce)
                if flag == True:
                    _configFile.close()
                    _tmpConfigFile.close()
                    os.remove(path + 'config.tmp')
                else:
                    _configFile.close()

                return

            finally:

                _videoFile.close()
                _thumbFile.close()

                if flag == True and not _tmpConfigFile.closed:

                    print('Atualizando .cfg...')
                    self.updateCfgFile(_tmpConfigFile, _configFile)
                    print('Atualização realizada com sucesso!')

                if self.tracker != None:
                    self.tracker.progress.destroy()

                ftp.quit()

            self.updateListBoxUpload()

        if self.cfgLineCount(_configFile) == 2:
            _configFile.close()
            os.remove(path + 'config.cfg')
        else:
            _configFile.close()

        if flag == True:
            _tmpConfigFile.close()
            os.remove(path + 'config.tmp')

        messagebox.showinfo('AnieZilla', 'Todos os uploads terminaram!')

    def cfgSelectEntry(self, path, cfgFile):
        """ Method chooses the right lines of info in the .cfg file for the episodes selected. """

        episodeNumbers = self.controller.frames[directoryPage].episodeNumbers

        print('EpisodeNumbers in cfgSelecEntry: ', episodeNumbers)
        
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

        print('EpisodeNumbers in episodeNumbers verify: ', episodeNumbers)

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

        if i == len(self.fileList):
            i = 0
        elif i < len(self.fileList):
            i = 1
        elif i > len(self.fileList):
            i = -1
        elif i == 0:
            i = 2

        cfgFile.seek(0)

        return i

    def cancelUpload(self):
        ...

    def pauseUpload(self):
        ...

    def helpWindow(self, parent):
        
        win = Toplevel(parent)
        win.geometry('250x250')
        win.resizable(0, 0)
        win.title('Página de Ajuda AnieZilla')
        Label(win, text = 'Teste').pack()

    def updateListBoxUpload(self):
        """ Method updates the Listbox of the progress on de episodes uploads. """
        
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
        """ Method fills the Listbox with the selected episodes for upload. """

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
