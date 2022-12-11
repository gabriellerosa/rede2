#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import random
import pickle
import inquirer

from rich.console import Console
from rich.text import Text
from rich.emoji import Emoji


from game import Game
from config import *

console = Console()

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
hard_words = open('./database/hard.txt', 'r', encoding='utf-8').readlines()
medium_words = open('./database/medium.txt', 'r', encoding='utf-8').readlines()

# Palavra secreta do dia
hard_day_word = hard_words[random.randint(0, len(hard_words))]
medium_day_word = medium_words[random.randint(0, len(medium_words))]

# Dicionario que vai guardar o endereço do cliente e o objeto game
address_game = dict()
connected_clients = dict()

def accept_wrapper(sock):
    
    conn, addr = sock.accept()  # Should be ready to read
    
    print(f"Accepted connection from {addr}")
    
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    selector.register(conn, events, data=data)

    # Criando o jogo
    address_game[addr] = Game()
    
    # Adicionando o cliente na lista de clientes conectados
    connected_clients[addr] = conn
    
    new_game_message = pickle.dumps({
        'type': 'nickname_selection',
        'content': 'Escolha um nickname para começar a jogar!',
    })
    
    conn.send(new_game_message)
    
    

def service_connection(key, mask):

    socket = key.fileobj
    data = key.data
    
    # int: o que vamos retornar para o cliente
    if mask & selectors.EVENT_READ:
        received_message = socket.recv(BUFF_SIZE)  # Should be ready to read
        client_addr = data.addr
        client_game = address_game[client_addr]
        
        if received_message:
            received_message = pickle.loads(received_message)
            
            if(received_message['type'] == 'nickname_selection'):
                client_game.set_nickname(received_message['content'])
                
                text = Text("Novo usuário: ")
                text.append(Text.assemble(received_message['content'], style="bold blue"))
                text.append(" | Endereço: " + str(client_addr))
                
                console.log(text)
                
                
                message = pickle.dumps({
                    'type': 'difficulty_selection',
                    'content': 'Selecione o nível de dificuldade',
                    'options': ['Médio', 'Difícil']
                })
                
                socket.send(message)
                
            
            elif(received_message['type'] == 'difficulty_selection'):
                client_game.set_difficulty(received_message['content'])
                client_game.set_secret_word(hard_day_word, medium_day_word)
                
                text = Text()
                text.append(Text.assemble(client_game.nickname, style="bold blue"))
                text.append(" selecionou o nível " + received_message['content'])
                
                console.log(text)
                
                
                message = pickle.dumps({
                    'type': 'guess',
                    'content': 'Adivinhe a palavra',
                    'board': client_game.show()
                })
                
                socket.send(message)
                
            elif (received_message['type'] == 'guess'):
                result = client_game.guess(received_message['content'])
                board = client_game.show()
                
                text = Text("Tentativa de ")
                text.append(Text.assemble(client_game.nickname, style="bold blue"))
                text.append(": " + received_message['content'])
                
                console.log(text)
                
                # if result == 'Você acertou!':
                #     # Envia mensagem para todos os clientes
                #     for client in connected_clients:
                #         received_message = pickle.dumps({
                #             'type': 'update',
                #             'content': f'{client_game.nickname} acertou a palavra'
                #         })
                        
                #         connected_clients[client].send(received_message)
                        
                
                message = pickle.dumps({
                    'type': 'guess_result',
                    'content': result,
                    'board': board
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
            socket.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print("Sent from", data.addr)
            print(f"Echoing {data.outb!r} to {data.addr}")
            
            sent = socket.send(data.outb)  # Should be ready to write
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
        print("Caught keyboard interrupt, exiting")
        
    finally:
        selector.close()
        socket.close()
