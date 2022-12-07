import unicodedata
from termcolor import colored

class Game:

    def __init__(self):
        
        self.attempts = 0 # int: Qnt de tentativas que a pessoa fez
        self.game_difficulty = 'easy'
        self.game_over = False
        self.need_coloring = False # Se a última tentativa foi boa TRUE senao FALSE
        self.secret_word = ""
        self.tabuleiro = []

    # Recebe uma word que é a string que representa o palpite feito pelo client
    def guess(self, word):
        
        if(self.game_over):
            return "5" # 'O jogo já acabou'
        
        # só devemos adicionar a palavra se ela for de fato uma palavra de tamanho 5
        if(len(word) != 5):
            return "4" # Palavra nao permitida
            
        # Palavra válida, então será necessário colorí-la
        self.need_coloring = True
        self.tabuleiro.append(word)
        
        # Ignora os acentos da palavra secreta. Ex: ética -> etica
        word_without_accent = unicodedata.normalize(
            'NFKD', self.secret_word).encode('ASCII', 'ignore').decode()
        
		# Se as palavras forem iguais, logo o jogo acaba pois a pessoa ganhou
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
    
    # A palavra a ser comparada depende do nivel de dificuldade.
    # Se for difícil, os acentos são considerados.
    def get_word_to_be_compared(self):
        
        if(self.game_difficulty == 'hard'):
            return self.secret_word
        
        return unicodedata.normalize(
        'NFKD', self.secret_word).encode('ASCII', 'ignore').decode()
