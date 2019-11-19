from tqdm import tqdm
from re import search
from time import sleep
from subprocess import call
from os import rename, remove, listdir, getcwd, sep, system

images = ['.png', '.jpg', '.jpeg']

def get_directory():
    'Takes a path directory from the user and returns it.'

    path = input('Digite o diretório: ')
    if path:
        path = path + sep
    else:
        path = getcwd() + sep
        print('Usando diretório atual: ', path)

    return path

def get_filter():
    'Takes an extension name and returns it.'

    pattern = input('Filtrar por: ')
    return pattern

def init():
    'Initializes the variables in the main code.'

    path = get_directory()
    pattern = get_filter()
    extension = '.' + pattern
    return path, pattern, extension

def f_rename(lst, path, name, extension, c = 1):
    "Rename all the files in 'path' described in 'lst'."

    option = input('Tem certeza que deseja renomear todos os arquivos do diretório?[s/n]: ')
    
    if option in 'Ss' or not option:
        system('clear')
        print('\nRenomeando todos os arquivos do diretório\n')
        for i in tqdm(lst):
            rename(path + i, path + name + str(c) + extension)
            c = c + 1
        print('Todos os arquivos foram renomeados!\n')
    else:
        system('clear')
        return None

def f_redim(lst, path, name, extension, c = 1, erase = ''):
    '''
    Function resizes all image files in 'path' described in 'lst' to a width chosen by the user
    (height will be proportional). The default behavior is to erase the original file after resizing it.
    '''

    width = input('Digite a largura da imagem: ')
    option = input('Tem certeza que deseja redimensionar todas as imagens no diretório?[s/n]: ')

    if option in 'Ss' or not option:
        system('clear')
        print('\nRedimensionando todas as imagens...')
        for i in tqdm(lst):
            call(['ffmpeg', '-i', i, '-hide_banner', '-loglevel', 'panic', '-vf', 'scale=' + width + ':-1', name + str(c) + extension], cwd = path)
            if not erase:
                remove(path + i)
            c = c + 1
        print('Todas as imagens foram redimensionadas!\n')
    else:
        system('clear')
        return None

def f_convert(lst, path, name):
    '''
    Uses FFmpeg to convert all video files in 'path' described in 'lst' to an output_format of user's choice.
    The standard behavior is to consider that there is a subtitle that needs to be hardcoded into the output video.
    '''

    output_format = input('Qual o formado da saída? ')
    option = input('Tem certeza que deseja converter todos os arquivos do diretório para' + ' .' + output_format + '?[s/n]: ')

    if option in 'Ss' or not option:
        system('clear')
        print('Convertendo todos os arquivos...\n')
        for i in tqdm(lst):
            call(['ffmpeg', '-i', i, '-hide_banner', '-loglevel', 'panic', '-vf', 'subtitles=' + i, i[:-3] + output_format], cwd = path)
        print('Todos os arquivos foram convertidos!\n')
    else:
        system('clear')
        return None

def print_file_list(lst):
    'Prints the files in directory.'

    print('')
    print('Lista de arquivos encontrados:\n')
    for i in lst:
        print(i)
    print('')

def filter_pattern(pattern, directory):
    'Uses RegEx to filter a file extension pattern in the directory and return a list of files only with that extension pattern.'

    return [i for i in directory if search(pattern, i)]

def make_directory_list(path):
    "Takes a path and returns a list of files in it."

    return listdir(path)

def output_name(extension):
    "Returns the name of the file based on the extension user wants to filter."

    if extension in images:
        return 'thumb-'
    else:
        return 'episodio-'

def file_list(path, pattern):
    "Returns a list of files in 'path' that matches a given extension pattern."

    lista = filter_pattern(pattern, make_directory_list(path))
    lista.sort()
    return lista

def list_test(lst):
    if lst:
        print_file_list(lst)
    else:
        print('\nNão há arquivos com essa extensão no diretório.\n')

