
import socket
import os
import pickle
import inquirer
import unicodedata
import time

from rich.console import Console
from rich.text import Text
import rich.spinner as spinner
from rich import box
from rich.table import Table
from termcolor import colored

from config import *

console = Console()

wordle = '[green]W[yellow]O[white]R[green]D[yellow]L[white]E'
selected_difficulty = None

def remove_accents(word):
    
    return unicodedata.normalize('NFKD', word).encode('ASCII', 'ignore').decode()
    
def show_table(board, secret_word):
    
    print('\n\n')
    table = Table(
                  show_header=False, 
                  title=wordle, 
                  box=box.SQUARE, 
                  show_lines=True, 
                )
    
    for tried_word in board:
        validated_word = list()
        
        for i in range(len(tried_word)):
            color = 'white'
            
            # Se a dificuuldade for média, compara-se as letras ignorando os acentos
            if selected_difficulty == 'Média':
                # tried_word[i] sem acento
                if(remove_accents(tried_word[i]) == remove_accents(secret_word[i])):
                    color = 'green'
                elif remove_accents(tried_word[i]) in remove_accents(secret_word):
                    color = 'yellow'
                
            else:
                if(tried_word[i] == secret_word[i]):
                    color = 'green'
                elif tried_word[i] in secret_word:
                    color = 'yellow'
                    
            validated_word.append({
                'letter': tried_word[i],
                'color': color
            })
            
        table.add_row(
            *[
                Text(
                    letter['letter'], 
                    style='bold ' + letter['color']
                    ) 
                for letter in validated_word
            ], 
        )
        
    for i in range(len(board), 6):
        table.add_row(*[f" " for letter in secret_word])
        
    console.print(table, justify='center')
    
    print('\n\n')

def clearConsole():
    
    command = 'clear'
    
    # Verifica se o sistema operacional é Windows
    if os.name in ('nt', 'dos'):  
        command = 'cls'

    os.system(command)

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
    console.log('[bold green]Conexão estabelecida com o servidor! :white_check_mark:')
    time.sleep(1)
    
except ConnectionRefusedError:
    console.log('O servidor não está rodando!', style='bold red')
    exit()


while True:
    clearConsole()
    
    # Mensagem recebida do servidor
    received_message = socket.recv(BUFF_SIZE)
    
    # Carrega o dicionario usando pickle.loads()
    received_message = pickle.loads(received_message)
    msg_type = received_message['type']
    
    # Dicionário que será enviado ao servidor
    message = dict()
    message['type'] = ''
    message['content'] = ''
    
    # Escolha de nickname
    if(msg_type == 'nickname_selection'):
        console.print('Bem vindo ao ' + wordle + '!\n')
        print('Escolha um nickname para começar a jogar!\n')
        
        nickname = input('Nickname: ')
        
        message['type'] = 'nickname_selection'
        message['content'] = nickname
       
    # Escolha de dificuldade 
    elif(msg_type == 'difficulty_selection'):
        questions = [inquirer.List(
                                   'difficulty', 
                                    message=received_message['content'], 
                                    choices=['Médio', 'Difícil'], 
                                    carousel=True
                                    )]
        
        selected_difficulty = inquirer.prompt(questions)['difficulty']
        
        colored_difficulty = colored(
                                    selected_difficulty, 
                                    'green' if selected_difficulty == 'Médio' 
                                    else 'red'
                                    )
        
        print('Você escolheu a dificuldade ' + colored_difficulty + '!\n')
        
        message['type'] = 'difficulty_selection'
        message['content'] = selected_difficulty
        
    # Tentativa de adivinhação
    elif(msg_type == 'guess'):
        show_table(received_message['board'], received_message['secret_word'])
        
        print()
        guess = input('Sua tentativa: ').strip().replace(' ', '').upper()
        
        message['type'] = 'guess'
        message['content'] = guess
    
    # Resultado da tentativa
    elif(msg_type == 'guess_result'):
        show_table(received_message['board'], received_message['secret_word'])
        
        print()
        if(received_message['content']['game_over']):
            
            if(not received_message['content']['winner']):
                console.print('Suas tentativas se esgorataram! :disappointed:', justify='center', style='bold red')
                console.print('A palavra era: [bold green]' + received_message['secret_word'], justify='center')
                
            else:
                console.print('Parabéns, você acertou! :tada: :tada: :smiley:', justify='center', style='bold green')
            
            print('\n\n')
            
            message['type'] = 'game_over'
            message['content'] = ''
            
            message = pickle.dumps(message)
            socket.send(message)
            
            break
        
        
        console.print(received_message['content']['message'], justify='center', style='bold red')
        
        print('\n\n')
        
        guess = input('Sua tentativa: ')
        guess = guess.strip().replace(' ', '').upper()
    
        message['type'] = 'guess'
        message['content'] = guess
    
    # Envia a mensagem ao servidor    
    message = pickle.dumps(message)
    socket.send(message)


