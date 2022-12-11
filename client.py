
import socket
import os
import pickle
import inquirer

from config import *
from termcolor import colored

# Criar um socket TCP/IP
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar o socket no host e porta especificados
socket.connect((HOST, PORT))

def clearConsole():
    
    command = 'clear'
    # verificando qual o tipo de sistema operacional
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'

    # isso é como se a gt estivesse escrevendo no terminal, mas a maquina que escreve que maneiro =D
    os.system(command)

while True:
    # Limpar console
    clearConsole()
    
    # Mensagem recebida do servidor
    received_message = socket.recv(BUFF_SIZE)
    
    # Carrega o dicionario usando pickle.loads()
    received_message = pickle.loads(received_message)
    
    # print(received_message)
    
    # Escolha de nickname
    if(received_message['type'] == 'nickname_selection'):
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
    elif(received_message['type'] == 'difficulty_selection'):
        questions = [
        inquirer.List('difficulty',
                        message=received_message['content'],
                        choices=['Normal', 'Difícil'],
                    ),
        ]
        
        selected_difficulty = inquirer.prompt(questions)['difficulty']
        
        print('Você escolheu a dificuldade ' + colored(selected_difficulty, "green" if selected_difficulty == 'Normal' else 'red') + '!\n')
        
        # Send the difficulty to the server
        
        message = pickle.dumps({
            'type': 'difficulty_selection',
            'content': selected_difficulty
        })
        
        socket.send(message)
        
    elif(
        received_message['type'] == 'guess'
    ):
        print(received_message['board'])
        print(received_message['content'])
        
        if received_message['content'] == 'Você acertou!':
            break
        
        guess = input()
        
        # Send the difficulty to the server
        message = pickle.dumps({
            'type': 'guess',
            'content': guess
        })
        
        socket.send(message)
    
    elif(
        received_message['type'] == 'guess_result'
    ):
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
            print(received_message['content']['message'])
            print(received_message['board'])
            
            guess = input('Digite a palavra: ')
        
            message = pickle.dumps({
                'type': 'guess',
                'content': guess
            })
            
            socket.send(message)
                    
    elif(
        received_message['type'] == 'update'
    ):
        print(received_message['content'])
    else:
        print('Erro desconhecido')  

