
import socket
import os
import pickle
import inquirer

from rich.console import Console
from rich.text import Text
from rich.emoji import Emoji
import rich.spinner as spinner
from rich import box
from rich.table import Table

from config import *
from termcolor import colored

import time

console = Console()

# Cria um socket TCP/IP
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta o socket no host e porta especificados
try: 
    with console.status('[bold green]Conectando-se ao servidor...') as status:
        spinner = spinner.Spinner('line')
    
        for _ in range(10):
            spinner.update()
            time.sleep(0.1)
            
    
    socket.connect((HOST, PORT))
    console.log('[bold green]Conexão com o servidor estabelecida! :white_check_mark:')
    time.sleep(1)
    
except ConnectionRefusedError:
    console.log('O servidor não está rodando!', style='bold red')
    exit()
    
    
def show_table(board, secret_word):
    table = Table(show_header=False, title="WORDLE", box=box.SQUARE, show_lines=True, header_style="bold magenta")
    
    for tried_word in board:
        validated_word = list()
        
        for i in range(len(tried_word)):
            if(tried_word[i] == secret_word[i]):
                validated_word.append({
                    'letter': tried_word[i], 
                    'color': 'green'})
            elif tried_word[i] in secret_word:
                validated_word.append({
                    'letter': tried_word[i], 
                    'color': 'yellow'})
            else:
                validated_word.append({
                    'letter': tried_word[i], 
                    'color': 'white'})
                
            
        table.add_row(
            *[Text(letter['letter'], style='bold ' + letter['color']) for letter in validated_word], 
        )
        
    for i in range(len(board), 6):
        table.add_row(*[f" " for letter in secret_word])
        
    console.print(table)


def clearConsole():
    
    command = 'clear'
    # verificando qual o tipo de sistema operacional
    
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'

    # isso é como se a gt estivesse escrevendo no terminal, mas a maquina que escreve que maneiro =D
    os.system(command)

while True:
    # Limpa o console
    clearConsole()
    
    # Mensagem recebida do servidor
    received_message = socket.recv(BUFF_SIZE)
    
    # Carrega o dicionario usando pickle.loads()
    received_message = pickle.loads(received_message)
    msg_type = received_message['type']
    
    # Escolha de nickname
    if(msg_type == 'nickname_selection'):
        wordle = 'Wordle'
        colored_wordle = ""
        colors = ['green', 'yellow', 'white']
        
        for i in range(len(wordle)):
            colored_wordle += colored(wordle[i], colors[i % len(colors)])
            
        print('Bem vindo ao ' + colored_wordle + '!\n')
        print('Escolha um nickname para começar a jogar!\n')
        
        nickname = input('Nickname: ')
        
        # Send the nickname to the server
        message = pickle.dumps({
            'type': 'nickname_selection',
            'content': nickname
        })
        
        socket.send(message)
       
    # Seleção de dificuldade 
    elif(msg_type == 'difficulty_selection'):
        questions = [
        inquirer.List('difficulty',
                        message=received_message['content'],
                        choices=['Normal', 'Difícil'],
                    ),
        ]
        
        selected_difficulty = inquirer.prompt(questions)['difficulty']
        
        print('Você escolheu a dificuldade ' + colored(selected_difficulty, "green" if selected_difficulty == 'Normal' else 'red') + '!\n')
        
        message = pickle.dumps({
            'type': 'difficulty_selection',
            'content': selected_difficulty
        })
        
        socket.send(message)
        
    elif(msg_type == 'guess'):
        console.log(received_message)
        show_table(received_message['board'], received_message['secret_word'])
        
        if received_message['content'] == 'Você acertou!':
            break
        
        guess = input().strip().replace(' ', '').upper()
        
        # Send the difficulty to the server
        message = pickle.dumps({
            'type': 'guess',
            'content': guess
        })
        
        socket.send(message)
    
    elif(msg_type == 'guess_result'):
        
        show_table(received_message['board'], received_message['secret_word'])
        
        if(received_message['content']['game_over']):
            print(received_message['content']['message'])
            
            if(not received_message['content']['winner']):
                print('A palavra era: ' + received_message['content']['secret_word'])
                
            message = pickle.dumps({
                'type': 'game_over',
                'content': ''
            })
            
            socket.send(message)
            
            break
        else:
            guess = input('Digite a palavra: ').strip().replace(' ', '').upper()
        
            message = pickle.dumps({
                'type': 'guess',
                'content': guess
            })
            
            socket.send(message)
                    
    elif(
        msg_type == 'update'
    ):
        print(received_message['content'])
    else:
        print('Erro desconhecido')  

