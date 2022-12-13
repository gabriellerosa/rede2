import socket
import selectors
import types
import random
import pickle
import time

from rich.console import Console
from rich.text import Text
import rich.spinner as spinner

from game import Game
from config import *

console = Console()

# Criar um socket TCP/IP
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    with console.status('[bold green]Iniciando o servidor...') as status:
        spinner = spinner.Spinner('line')
        
        for _ in range(10):
            spinner.update()
            time.sleep(0.2)
            
    
    # Conecta o socket no host e porta especificados
    socket.bind((HOST, PORT))

    # Atende as conexões recebidas
    socket.listen(1)

    console.log(':running: Ouvindo conexões em ' + 
                str(socket.getsockname()), style='bold')

    # Chamadas de socket não mais serão bloqueantes
    socket.setblocking(False)

    selector = selectors.DefaultSelector()

    # Registra o socket para receber eventos de leitura
    selector.register(socket, selectors.EVENT_READ, data=None)
    
    console.log('[bold green]Servidor iniciado com sucesso! :white_check_mark:')
    
except OSError:
    console.log('O servidor já está sendo executado no host e porta especificados. :x:', 
                style='bold red')
    exit()

hard_words = open('./database/hard.txt', 'r', encoding='utf-8').readlines()
medium_words = open('./database/medium.txt', 'r', encoding='utf-8').readlines()

# Palavra secreta do dia
hard_day_word = hard_words[random.randint(0, len(hard_words))].strip()
medium_day_word = medium_words[random.randint(0, len(medium_words))].strip()

# Dicionarios que armazenarão o endereço do cliente seu respectivo jogo
game_address = dict()
connected_clients = dict()

def accept_wrapper(sock):
    
    conn, addr = sock.accept() 
    conn.setblocking(False)
    
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    selector.register(conn, events, data=data)
    
    addr_str = f'{addr[0]}:{addr[1]}'

    # Criando o jogo
    game_address[addr_str] = Game()
    
    # Adicionando o cliente na lista de clientes conectados
    connected_clients[addr_str] = conn
    
    new_game_message = pickle.dumps({
        'type': 'nickname_selection',
        'content': 'Escolha um nickname para começar a jogar!',
    })
    
    conn.send(new_game_message)
    
    console.log(f'[bold green]Conexão aceita de {addr[0]}:{addr[1]}')
    

def service_connection(key, mask):

    socket = key.fileobj # socket do cliente que enviou a mensagem 
    data = key.data # dados do cliente que enviou a mensagem 
    
    # Se o evento for de leitura, então o cliente enviou uma mensagem
    if mask & selectors.EVENT_READ:
        received_message = socket.recv(BUFF_SIZE)
        
        client_addr = data.addr
        client_addr = f'{client_addr[0]}:{client_addr[1]}'
        client_game = game_address[client_addr]
        
        if received_message:
            received_message = pickle.loads(received_message)
            
            if(received_message['type'] == 'nickname_selection'):
                client_game.set_nickname(received_message['content'])
                
                text = Text("Novo usuário: ")
                text.append(Text.assemble(received_message['content'], 
                                          style="bold blue"))
                text.append(" | Endereço: " + client_addr)
                
                console.log(text)
                
                message = pickle.dumps({
                    'type': 'difficulty_selection',
                    'content': 'Selecione o nível de dificuldade',
                    'options': ['Médio', 'Difícil']
                })
                
                socket.send(message)
            
            elif(received_message['type'] == 'difficulty_selection'):
                client_game.set_difficulty(received_message['content'])
                client_game.set_secret_word(medium_day_word, hard_day_word)
                
                text = Text()
                text.append(Text.assemble(client_game.nickname, style="bold blue"))
                text.append(" selecionou o nível " + received_message['content'])
                
                console.log(text)
                console.log("Palavra secreta: [bold green]", client_game.secret_word)
                
                message = pickle.dumps({
                    'secret_word': client_game.secret_word,
                    'type': 'guess',
                    'content': 'Adivinhe a palavra',
                    'board': client_game.show(),
                })
                
                socket.send(message)
                
            elif (received_message['type'] == 'guess'):
                result = client_game.guess(received_message['content'])
                board = client_game.show()
                
                text = Text("Tentativa de ")
                text.append(Text.assemble(client_game.nickname, style="bold blue"))
                text.append(": " + received_message['content'])
                
                console.log(text)
                
                message = pickle.dumps({
                    'type': 'guess_result',
                    'content': result,
                    'board': board,
                    'secret_word': client_game.secret_word,
                })
                
                socket.send(message)

            elif (received_message['type'] == 'game_over'):
                text = Text(client_game.nickname)
                text.stylize("bold blue")
                text.append(" saiu do jogo.")
                
                console.log(text)
                
                # Remove o cliente da lista de clientes conectados
                connected_clients.pop(client_addr)
                
                # Remove o cliente da lista de seletores
                selector.unregister(socket)
                
        else:
            text = Text(client_game.nickname)
            text.stylize("bold blue")
            text.append(" saiu do jogo.")
            
            console.log(text)
            
            selector.unregister(socket)
            connected_clients.pop(client_addr)
            socket.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print("Sent from", data.addr)
            print(f"Echoing {data.outb!r} to {data.addr}")
            
            sent = socket.send(data.outb)
            data.outb = data.outb[sent:]
            
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
        console.log('Saindo... :wave:')
        
    finally:
        selector.close()
        socket.close()
