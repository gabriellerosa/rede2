#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import random

from game import Game
from config import *

# Criar um socket TCP/IP
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta o socket no host e porta especificados
socket.bind((HOST, PORT))

# Atende as conexões recebidas
socket.listen(1)

print('Servidor rodando em', socket.getsockname())

# Chamadas de socket não mais serão bloqueantes
socket.setblocking(False)

selector = selectors.DefaultSelector()

# Registra o socket para receber eventos de leitura
selector.register(socket, selectors.EVENT_READ, data=None)

# To do: Permitir que o cliente escolha o nível de dificuldade
list_of_words = open('./database/easy.txt', 'r', encoding='utf-8').readlines()

# Palavra secreta do dia
day_word = list_of_words[random.randint(0, len(list_of_words))]
day_word = day_word.strip().upper()

# Dicionario que vai guardar o endereço do cliente e o objeto game
address_game = dict()

def accept_wrapper(sock):
    
    conn, addr = sock.accept()  # Should be ready to read
    
    print(f"Accepted connection from {addr}")
    
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    selector.register(conn, events, data=data)

    # Criando o jogo
    address_game[addr] = Game()
    address_game[addr].secret_word = day_word


def service_connection(key, mask):

    socket = key.fileobj
    data = key.data

    # int: o que vamos retornar para o cliente
    if mask & selectors.EVENT_READ:
        recv_data = socket.recv(BUFF_SIZE)  # Should be ready to read
        if recv_data:

            # recv_data.decode() = palavra que o cliente enviou
            result = address_game[data.addr].guess(recv_data.decode())

            board = address_game[data.addr].show()

            data.outb = str.encode(result + board)
            #data.outc = str.encode(board)

        else:
            print(f"Closing connection to {data.addr}")
            selector.unregister(socket)
            socket.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = socket.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

            # print(data.outc.decode())
            # sentc = socket.send(data.outc)  # Should be ready to write

            # print('oi')
            # print(sentc)
            # data.outc = data.outb[sentc:]

if __name__ == "__main__":
    try:
        while True:
            events = selector.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)

    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
        
    finally:
        selector.close()
        socket.close()
