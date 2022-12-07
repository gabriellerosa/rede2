# Wordle 
Trata-se da implementação do Wordle, um jogo de advinhação de palavras, utilizando o Socket TCP. Este projeto representa a atividade prática sobre a Camada de Transporte realizada na disciplina 'CET098 - Rede de Computadores I' no semestre 2022.2. 

Nesta implementação, o servidor escolhe uma palavra secreta aleatória de cinco letras da língua portuguesa, enquanto o cliente deve tentar adivinhá-la, restrito a 6 tentativas. 

## 🚀 Executando o projeto

Para a execução do projeto, é necessário ter o Python instalado em sua máquina e pip, seu gerenciador de pacotes. Para isso, acesse o site oficial do Python e siga as instruções de instalação para o seu sistema operacional: https://www.python.org/downloads/.


#### Na pasta raiz do projeto, inicialize o ambiente virtual do Python

No Windows: 
```
py -m venv venv ; venv\Scripts\activate
```

Em distros Linux: 
```
python3 -m venv venv && source venv/bin/activate
```

#### Instale as dependências:
```
pip install -r requirements.txt
```

#### Executando servidor e cliente:

Os processos do servidor e cliente devem ser executados em abas distintas do terminal, nesta ordem:

Servidor:
```
python3 server.py localhost 50000
``` 

Cliente:
```
python3 client.py
```


## Discentes
<ul>
  <li>Gabrielle Rosa</li>
  <li>Daniel Jackson</li>
</ul>