import unicodedata

dictionary = open('./database/hard.txt', 'r', encoding='utf-8').readlines()
dictionary = [word.strip().upper() for word in dictionary]

class Game:

    def __init__(self):
        
        self.attempts = 0 # Número de tentativas
        self.secret_word = "" # Palavra a ser adivinhada
        self.board = [] # Lista de palavras tentadas
        self.difficulty = "" 
        self.nickname = ""

    # Recebe uma word que é a string que representa o palpite feito pelo client
    def guess(self, guessed_word):
        
        validation = self.validate_word(guessed_word)
        
        if(not validation['ok']):
            return {
                'game_over': False,
                'message': validation['message']
            }
            
        if (guessed_word in self.board):
            return {
                'game_over': False,
                'message': 'Você já tentou essa palavra!'
            }
        
        # É uma tentativa válida. Adiciona a palavra à lista de tentativas
        self.board.append(guessed_word)
        
        secret_word = self.get_word_to_be_compared()
        
        if(self.difficulty == 'Médio'):
            guessed_word = unicodedata.normalize('NFKD', guessed_word).encode('ASCII', 'ignore').decode()
        
		# Se as palavras forem iguais, logo o jogo acaba pois a pessoa ganhou
        if (guessed_word == secret_word):
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
                }
         
            return {
                    'game_over': False,
                    'message': 'Palavra incoreta :( Tente novamente!'
                }


    def show(self):
        return self.board
    
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        
    def set_secret_word(self, normal_level_word, hard_level_word):
        if self.difficulty == 'Médio':
            self.secret_word = normal_level_word
        else:
            self.secret_word = hard_level_word
    
    # A palavra a ser comparada depende do nivel de dificuldade.
    # Se for difícil, os acentos são considerados.
    def get_word_to_be_compared(self):
        
        if(self.difficulty == 'Médio'):
            # Remove acentos e outros caracteres especiais
            return unicodedata.normalize('NFKD', self.secret_word).encode('ASCII', 'ignore').decode()
        
        return self.secret_word
        
    def validate_word(self, word):
        
        if(len(word) != 5):
            return {
                'ok': False,
                'message': 'A palavra deve conter 5 letras'
            }

        if(not word.isalpha()):
            return {
                'ok': False,
                'message': 'A palavra deve conter apenas letras'
            }
        
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


        
        
        
        
