import unicodedata
from termcolor import colored

dictionary = open('./database/hard.txt', 'r', encoding='utf-8').readlines()
dictionary = [word.strip().upper() for word in dictionary]

class Game:

    def __init__(self):
        
        self.attempts = 0 # int: Qnt de tentativas que a pessoa fez
        self.secret_word = ""
        self.board = []
        self.difficulty = ""
        self.nickname = ""

    # Recebe uma word que é a string que representa o palpite feito pelo client
    def guess(self, word):
        
        validation = self.validate_word(word)
        
        if(not validation['ok']):
            return {
                'game_over': False,
                'message': validation['message']
            }
        
            
        # Palavra válida, então será necessário colorí-la
        self.board.append(word)
        
        # Ignora os acentos da palavra secreta. Ex: ética -> etica
        word_without_accent = unicodedata.normalize(
            'NFKD', self.secret_word).encode('ASCII', 'ignore').decode()
        
		# Se as palavras forem iguais, logo o jogo acaba pois a pessoa ganhou
        if (word == word_without_accent):
            return {
                'game_over': True,
                'winner': True,
                'message': 'Parabéns! Você ganhou!'
            }
        else:
            self.attempts += 1
            
            if (self.attempts >= 6):
                return {
                    'game_over': True,
                    'winner': False,
                    'message': 'Que pena! Suas tentativas se esgotaram',
                    'secret_word': self.secret_word
                }
         
            return {
                    'game_over': False,
                    'message': 'Tente novamente!'
                }


    def show(self):
        return self.board
    
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        
    def set_secret_word(self, normal_word, hard_word):
        self.secret_word = normal_word if self.difficulty == 'Normal' else hard_word
    
    # A palavra a ser comparada depende do nivel de dificuldade.
    # Se for difícil, os acentos são considerados.
    def get_word_to_be_compared(self):
        
        if(self.difficulty == 'Normal'):
            return unicodedata.normalize(
            'NFKD', self.secret_word).encode('ASCII', 'ignore').decode()
        
        return self.secret_word
        
        
    def validate_word(self, word):
        
        # Se a palavra não for de tamanho 5, não é válida
        if(len(word) != 5):
            return {
                'ok': False,
                'message': 'A palavra deve conter 5 letras'
            }

        # Se a palavra não for composta apenas por letras, não é válida
        if(not word.isalpha()):
            return {
                'ok': False,
                'message': 'A palavra deve conter apenas letras'
            }
        
        # Se a palavra não for encontrada no dicionário, não é válida
        if(word.upper() not in dictionary):
            return {
                'ok': False,
                'message': 'A palavra não está no dicionário'
            }
        
        return {
            'ok': True
        }

    def set_nickname(self, nickname):
        
        self.nickname = nickname


        
        
        
        
