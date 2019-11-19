from func import *
from os import system

path, pattern, extension = init()

name = output_name(extension)
lista = file_list(path, '[.]' + pattern + '\\b')

list_test(lista)

print('O que você pretende fazer? \n')

while True:

    print('Renomear todos os arquivos -> 1 ')
    print('Redimensionar todos os arquivos de thumb -> 2 ')
    print('Converter todos os vídeos da pasta -> 3 ')
    print('Filtrar por outra extensão -> 4 ')
    print('Escolher outro diretório -> 5 ')
    print('Sair -> 6\n')
    
    option = int(input('Digite a opção: '))

    if option == 6:
        break
    
    if option not in [1, 2, 3, 4, 5]:
        system('clear')
        print('Escolha outra opção: ')

    if option == 1:
        f_rename(lista, path, name, extension)
    elif option == 2:
        f_redim(lista, path, name, extension)
    elif option == 3:
        f_convert(lista, path, name)
    elif option == 4:
        pattern = get_filter()
        lista = file_list(path, '[.]' + pattern + '\\b')
        list_test(lista)
    elif option == 5:
        path, pattern, extension = init()