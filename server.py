import sys
import socket
import selectors
import types
import random
import unicodedata

from termcolor import colored

# To do: Permitir que o cliente escolha o nível de dificuldade
list_of_words = open('./database/easy.txt', 'r', encoding='utf-8').readlines()

# Palavra secreta do dia
day_word = list_of_words[random.randint(0, len(list_of_words))]

# Dicionario que vai guardar o endereço do cliente e o objeto game
address_game = dict()

class Game:

    def __init__(self):
        
        self.attempts = 0 # int: Qnt de tentativas que a pessoa fez
        self.game_difficulty = 'easy'
        self.game_over = False
        self.need_coloring = False # Se a última tentativa foi boa TRUE senao FALSE
        self.tabuleiro = []

    # Recebe uma word que é a string que representa o palpite feito pelo client
    def guess(self, word):
        if(self.game_over):
            return "5" # 'O jogo já acabou'
        
        if(len(word) != 5):
            return "4" # Palavra nao permitida
            
        # Palavra válida, então será necessário colorí-la
        self.need_coloring = True
        self.tabuleiro.append(word)
        
        # Ignora os acentos da palavra secreta. Ex: ética -> etica
        word_without_accent = unicodedata.normalize(
            'NFKD', day_word).encode('ASCII', 'ignore').decode()
        
        if (word == word_without_accent):
            self.game_over = True
            return "1"  # 'Você ganhou'
        else:
            self.attempts += 1
            if (self.attempts >= 6):
                self.game_over = True
                return "2"  # 'Tentou todas as palavras e perdeu'
            
            return "3"  # 'Tentou uma palavra mas ela está errada'
        

    def colorize(self, word):
        
        # Texto colorido
        colored_text = ""
        
        # A palavra a ser comparada depende do nivel de dificuldade.
        # Se for difícil, os acentos são considerados.
        secret_word = self.get_word_to_be_compared()
    
        for i in range(len(word)):
            # Cor padrão da letra
            color = "white"
            
            if(word[i] == secret_word[i]):
                color = "green"
            elif(word[i] in secret_word):
                color = "yellow"
                
            colored_text += colored(word[i], color)

        return colored_text

    def show(self):
        
        # se a ultima tentativa foi valida
        if(self.need_coloring):
            # Colorir as palavras: Vamos colorir a ultima palavra adicionada
            self.tabuleiro[-1] = self.colorize(self.tabuleiro[-1])

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
    
    def get_word_to_be_compared(self):
        if(self.game_difficulty == 'hard'):
            return day_word
        else:
            return unicodedata.normalize(
            'NFKD', day_word).encode('ASCII', 'ignore').decode()


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

if __name__ == "__main__":
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
    
    

