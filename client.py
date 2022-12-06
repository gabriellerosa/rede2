
import socket

HOST = '127.0.0.1'
PORT = 50000

obj_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Pedir para conectar lá no servidor
obj_socket.connect((HOST, PORT))

while True:

    print('Díga a palavra ai vá')
    word = input()

    print('Encode:')
    print(word.encode())
# Enviar dados para o servidor, portanto, enviando a palavra
    obj_socket.send(word.encode())

# Receber os dados que vem do servidor ate tamanho X
    data = obj_socket.recv(1024)

    print('Menssagem ecoada:')
    print(data.decode())

    if(data.decode() == '1'):
        print('Ganhou')
    elif(data.decode() == '2'):
        print('Perdeu')
    else:
        print('Palavra errada')
