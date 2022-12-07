import socket
import os

HOST = '127.0.0.1'
PORT = 50000
BUFF_SIZE = 1024

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

if __name__ == "__main__":
    
    while True:
        
        print('Díga a palavra ai vá')
        word = input()

        # Enviar dados para o servidor, portanto, enviando a palavra
        socket.send(word.encode())

        # Receber os dados que vem do servidor ate tamanho X
        # resposta sobre a palavra que a gt enviou anteriormente
        response_word = socket.recv(BUFF_SIZE)

        print('Menssagem ecoada:')
        print(response_word.decode())

        # resposta sobre como o tabuleiro ficou e precisa decodar pois ele veio encodado
        board = socket.recv(BUFF_SIZE)

        # splitar pois estava em formato de string
        words_board = board.decode()

        # limpar console
        clearConsole()

        # printa o tabuleiro atual
        print('-------------------\n')
        print(words_board)
        print('-------------------\n')
        
        decoded_word = response_word.decode()
        
        if(decoded_word == "3"):
            print("Palavra errada")
        elif (decoded_word == "4"):
            print('A palavra deve conter 5 letras')
        else:
            if(decoded_word == "1"):
                print('Ganhou')
            elif (decoded_word == "2"):
                print('Perdeu')
            elif (decoded_word == "5"):
                print('Acabaram as tentativas')
            
            socket.close()
            break