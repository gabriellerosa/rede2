#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import random
import unicodedata

from termcolor import colored
from database import list_of_words

day_word = list_of_words[random.randint(0, len(list_of_words))]
address_game = dict()

class Game:
    tabuleiro = []
    attempt = 0 # int: Qnt de tentativas que a pessoa fez
    need_coloring = False # se a ultima tentativa foi boa TRUE senao FALSE

    # Recebe uma word que é a string que representa o palpite feito pelo client
    def guess(self,word):

        # só devemos adicionar a palavra se ela for de fato uma palavra de tamanho 5
        if(len(word) != 5):
            return "4" # Palavra nao permitida

        # palavra valida entao ela vai precisar colorir
        self.need_coloring = True
        self.tabuleiro.append(word)

        # funcao padrao python para ignorar o acento das palavras, portanto, ética == etica
        ignoring_accent = unicodedata.normalize('NFKD', day_word).encode('ASCII', 'ignore').decode()

        # Se as palavras forem iguais, logo o jogo acaba pois a pessoa ganhou
        if(word == ignoring_accent):
            return "1" # 'Voce ganhou'
        else:
            self.attempt+=1
            if(self.attempt < 6):
                return "3"  # 'Tentou uma palavra mas ela está errada'
            return "2"      # 'Tentou todas as palavras e perdeu'

    # retorna a ultima palavra a ser colorida (a ultima adicionada)
    def colorir(self, palavra):
        text = ""
        freq = dict()

        # Colocando as letras verdes
        for i in range(len(palavra)):
            ignoring_accent = unicodedata.normalize(
                'NFKD', day_word[i]).encode('ASCII', 'ignore').decode()

            if (palavra[i] != ignoring_accent):
                if not ignoring_accent in freq:
                    freq[ignoring_accent] = 0
                freq[ignoring_accent] += 1

        # Colocando as letras amarelas
        for i in range(len(palavra)):
            ignoring_accent = unicodedata.normalize(
                'NFKD', day_word[i]).encode('ASCII', 'ignore').decode()

            if (palavra[i] == ignoring_accent):
                text += colored(day_word[i], "green")
            elif (palavra[i] in freq):
                text += colored(palavra[i], "yellow")
            else:
                text += palavra[i]

        return text

    def show(self):

        # se a ultima tentativa foi valida
        if(self.need_coloring):
            # Colorir as palavras: Vamos colorir a ultima palavra adicionada
            self.tabuleiro[-1] = self.colorir(self.tabuleiro[-1])

        self.need_coloring = False

        # Transformar o array de strings numa string unica
        board = ""
        for i in self.tabuleiro:
            board += i
            board += "\n"

        # Condicao para evitar o envio do board vazio, pois o cliente vai continuar esperando um board e nunca chegará. O envio vazio pode acontecer quando a pessoa inicia com uma palavra invalida
        if(board == ""):
            return "/n"

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

            # recv_data.decode() = palavra que o cliente enviou
            result = address_game[data.addr].guess(recv_data.decode())

            board = address_game[data.addr].show()

            data.outb = str.encode(result + board)
            #data.outc = str.encode(board)

        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

            # print(data.outc.decode())
            # sentc = sock.send(data.outc)  # Should be ready to write

            # print('oi')
            # print(sentc)
            # data.outc = data.outb[sentc:]


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
