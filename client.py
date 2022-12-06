
import socket

HOST = '127.0.0.1'
PORT = 50000

obj_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Pedir para conectar lá no servidor
obj_socket.connect((HOST, PORT))

while True:

    print('Díga a palavra ai vá')
    word = input()

    # Enviar dados para o servidor, portanto, enviando a palavra
    obj_socket.send(word.encode())

    # Receber os dados que vem do servidor ate tamanho X
    # resposta sobre a palavra que a gt enviou anteriormente
    response_word = obj_socket.recv(1)

    print('Menssagem ecoada:')
    print(response_word.decode())

    # resposta sobre como o tabuleiro ficou e precisa decodar pois ele veio encodado
    board = obj_socket.recv(1024)

    # splitar pois estava em formato de string
    words_board = board.decode()

    # printa o tabuleiro atual
    print('-------------------\n')
    print(words_board)
    print('-------------------\n')

    if (response_word.decode() == "1"):
        print('Ganhou')
        obj_socket.close()
        break
    elif (response_word.decode() == "2"):
        print('Perdeu')
        obj_socket.close()
        break
    else:
        print('Palavra errada')
