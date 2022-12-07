# Projeto de Redes - Socket TCP

## 🚀 Executando o projeto

#### Na pasta raiz do projeto, inicialize o ambiente virtual do Python

No Windows: 
```
py -m venv venv ; venv\Scripts\activate
```

Em distros Linux: 
```
python3 -m venv venv && source venv/bin/activate
```

#### Instalando as dependências:
```
pip install -r requirements.txt
```

#### Executando servidor e cliente:

Os processos do cliente e do servidor serão executados em abas distintas do terminal

Servidor:
```
python3 server.py localhost 50000
``` 

Cliente:
```
python3 client.py
```