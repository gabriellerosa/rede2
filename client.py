
import socket
import os
from config import *

# Criar um socket TCP/IP
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar o socket no host e porta especificados
socket.connect((HOST, PORT))

def clearConsole():
    
    command = 'clear'
    # verificando qual o tipo de sistema operacional
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'

    # isso é como se a gt estivesse escrevendo no terminal, mas a maquina que escreve que maneiro =D
    os.system(command)

while True:

    word = input('Diga a palavra aí, vá:\n')
    
    word = word.strip().replace(' ', '').upper()
    
    if not word:
        continue

    # Enviar dados para o servidor, portanto, enviando a palavra
    socket.send(word.encode())

    # Receber os dados que vem do servidor ate tamanho X
    # resposta sobre a palavra que a gt enviou anteriormente
    # 1 = caracter inicial na resposta
    # 6 = tamanho maximo da palvra de retorno 5 + 1 que é o \n

    # portanto o tabuleiro todo preenchido = 6 * 6 + 1 = 37
    # resposta sobre como o tabuleiro ficou e precisa decodar pois ele veio encodado
    response = socket.recv(BUFF_SIZE).decode()

    print('Menssagem ecoada:')

    words_board = response[1:]
    option = response[0]

    # limpar console
    clearConsole()

    # printa o tabuleiro atual
    print('-------------------\n')
    print(words_board)
    print('-------------------\n')

    if (option == "1"):
        print('Ganhou')
        socket.close()
        break
    elif (option == "2"):
        print('Perdeu')
        socket.close()
        break
    elif (option == "3"):
        print('Palavra Errada')
    elif (option == "4"):
        print('Palavra Invalida')
    else:
        print('Número de tentativas esgotado')
        socket.close()
