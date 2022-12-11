import unicodedata
from termcolor import colored

dictionary = open('./database/hard.txt', 'r', encoding='utf-8').readlines()
dictionary = [word.strip().upper() for word in dictionary]



class Game:

    def __init__(self):
        
        self.attempts = 0 # int: Qnt de tentativas que a pessoa fez
        self.game_over = False
        self.need_coloring = False # Se a última tentativa foi boa TRUE senao FALSE
        self.secret_word = ""
        self.tabuleiro = []
        self.difficulty = ""
        self.nickname = ""

    # Recebe uma word que é a string que representa o palpite feito pelo client
    def guess(self, word):
        if(self.game_over):
            return {
                'game_over': True,
                'message': 'O jogo já acabou',
            }
        
        validation = self.validate_word(word)
        
        if(not validation['ok']):
            return {
                'game_over': False,
                'message': validation['message']
            }
        
            
        # Palavra válida, então será necessário colorí-la
        self.need_coloring = True
        self.tabuleiro.append(word)
        
        # Ignora os acentos da palavra secreta. Ex: ética -> etica
        word_without_accent = unicodedata.normalize(
            'NFKD', self.secret_word).encode('ASCII', 'ignore').decode()
        
		# Se as palavras forem iguais, logo o jogo acaba pois a pessoa ganhou
        if (word == word_without_accent):
            self.game_over = True
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

    def colorize(self, word):
        
        # Texto colorido
        colored_text = ""

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
    
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        
    def set_secret_word(self, normal_word, hard_word):
        self.secret_word = normal_word if self.difficulty == 'Normal' else hard_word
    
    # A palavra a ser comparada depende do nivel de dificuldade.
    # Se for difícil, os acentos são considerados.
    def get_word_to_be_compared(self):
        
        if(self.difficulty == 'hard'):
            return self.secret_word
        
        return unicodedata.normalize(
        'NFKD', self.secret_word).encode('ASCII', 'ignore').decode()
        
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


        
        
        
        
