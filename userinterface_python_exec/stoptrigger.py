import socket

def test_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 65432))

    messages = ["stoptrigger"]

    for message in messages:
        client_socket.sendall(message.encode())
        print(f"Sent: {message}")
        data = client_socket.recv(1024)
        print(f"Received acknowledgment: {data.decode()}")

    client_socket.close()

if __name__ == "__main__":
    test_server()