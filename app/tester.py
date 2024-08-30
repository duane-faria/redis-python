import socket
from app.resp_handlers import RESPEncoder

# Configurações do cliente
host = '127.0.0.1'  # Endereço IP do servidor
port = 6379        # Porta em que o servidor está escutando

# Criação do socket TCP/IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        message = input('insira a mensagem')
        # Conectando ao servidor
        client_socket.connect((host, port))
        print(f"Conectado ao servidor {host}:{port}")

        # Enviando uma mensagem para o servidor
        message = RESPEncoder.array_encode(message)
        client_socket.sendall(message.encode('utf-8'))
        print(f"Mensagem enviada: {message}")

        # Recebendo resposta do servidor
        response = client_socket.recv(1024)
        print(f"Resposta do servidor: {response.decode('utf-8')}")
    finally:
        # Fechando o socket
        client_socket.close()
        print("Conexão fechada.")

