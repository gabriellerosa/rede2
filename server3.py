#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import random

list_of_words = ["ética","plena","mútua","tênue","sutil","vigor","fazer","aquém","assim","porém","seção","audaz","sanar","cerne","fosse","inato","ideia","poder","moral","desde","justo","muito","torpe","honra"]
day_word = random.randint(0, len(list_of_words))
address_game = dict()

class Game:
    tabuleiro = []
    attempt = 0 # int: Qnt de tentativas que a pessoa fez
    end_game = 0 # int: 1 = jogo acabou

    def guess(self,word):

        self.tabuleiro.append(word)

        if(word == day_word):
            end_game = 1
            return "1" # 'Voce ganhou'
        else:
            self.attempt+=1
            if(self.attempt >= 5):
                end_game = 1
                return "2" # 'Tentou todas as palavras e perdeu'
            return "3"     # 'Palavra errada'

    def show(self):

        # Transformar o array de strings numa string unica
        board = ""
        for i in self.tabuleiro:
            board += i
            board += "\n"

        return board

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

    # Criando o jogo
    address_game[addr] = Game()


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    # int: o que vamos retornar para o cliente
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:

            result = address_game[data.addr].guess(recv_data.decode())
            board = address_game[data.addr].show()
            data.outb = str.encode(result)
            data.outc = str.encode(board)

        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

            print(data.outc.decode())
            sentc = sock.send(data.outc)  # Should be ready to write

            print('oi')
            print(sentc)
            data.outc = data.outb[sentc:]



if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
    lsock.close()
