import socket
import threading
import random
import os
import json
import time

# List of adjectives and nouns for random username generation
ADJECTIVES = ['Hurtig', 'Smuk', 'Glad', 'Rolig', 'Langsom']
NOUNS = ['Tiger', 'Hund', 'Kat', 'Haj', 'Ulv']

# Function to generate a random username
def generate_username():
    return random.choice(ADJECTIVES) + random.choice(NOUNS)

# Function to broadcast host details
def broadcast_host_details(broadcast_port, main_port, username):
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        host_details = {
            'username': username,
            'ip': socket.gethostbyname(socket.gethostname()),
            'port': main_port
        }
        message = json.dumps(host_details)
        broadcast_socket.sendto(message.encode('utf-8'), ('<broadcast>', broadcast_port))
        print(f"Broadcasting: {message}")
        time.sleep(2)  # Broadcast every 2 seconds

# Function to listen for broadcast messages
def listen_for_broadcasts(broadcast_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener_socket:
        listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener_socket.bind(('0.0.0.0', broadcast_port))
        listener_socket.settimeout(10)  # Timeout after 10 seconds

        try:
            while True:
                data, _ = listener_socket.recvfrom(1024)
                message = json.loads(data.decode('utf-8'))
                ip = message['ip']
                print(f"Received broadcast: {message}")
                print("Available host:")
                print(f"{message['username']} at {message['ip']}:{message['port']}")
                choice = input("Do you want to connect to this host? (yes/no): ").strip().lower()
                if choice == "yes":
                    return message  # Return the selected host
                else:
                    continue  # Continue listening for more hosts
        except socket.timeout:
            pass

    return None  # Return None if no hosts were selected

# Function to connect to a host server
def connect_to_host(host):
    host_ip = host['ip']
    port = host['port']

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host_ip, port))

    # Generate and send the client's username
    client_username = generate_username()
    client.send(client_username.encode('utf-8'))

    # Receive and display the server's username
    server_username = client.recv(1024).decode('utf-8')
    print(f"Connected to host. Your username: {client_username}, Host's username: {server_username}")

    while True:
        file_name = input("Enter the name of the .txt file to request: ")
        client.send(file_name.encode('utf-8'))

        response = client.recv(1024).decode('utf-8')
        if response == "FILE_FOUND":
            file_data = client.recv(4096)  # Adjust buffer size as needed
            with open(f"received_{file_name}", 'wb') as f:
                f.write(file_data)
            print(f"File '{file_name}' received and saved as 'received_{file_name}'.")
        else:
            print(f"File '{file_name}' not found on the host.")

# Function to handle client connection and file transfer
def handle_client(client_socket, address, server_username):
    print(f"[+] {address} connected.")
    client_username = client_socket.recv(1024).decode('utf-8')
    client_socket.send(server_username.encode('utf-8'))
    print(f"Client's username: {client_username}")

    while True:
        try:
            # Receive file request
            file_name = client_socket.recv(1024).decode('utf-8')
            if not file_name:
                break

            if os.path.exists(file_name):
                client_socket.send("FILE_FOUND".encode('utf-8'))
                with open(file_name, 'rb') as f:
                    file_data = f.read()
                    client_socket.send(file_data)
                print(f"File '{file_name}' sent to {client_username} at {address}.")
            else:
                client_socket.send("FILE_NOT_FOUND".encode('utf-8'))
                print(f"File '{file_name}' not found for {client_username} at {address}.")

        except ConnectionResetError:
            break

    print(f"[-] {address} disconnected.")
    client_socket.close()

# Function to start the server
def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)

    # Generate and display the server's username
    server_username = generate_username()
    print(f"Server's username: {server_username}")

    # Start broadcasting host details
    broadcast_thread = threading.Thread(target=broadcast_host_details, args=(5001, port, server_username))
    broadcast_thread.start()
    print("Broadcasting host details...")

    # Get and display the local IP address
    local_ip = socket.gethostbyname(socket.gethostname())
    print(f"[+] Server started on {local_ip}:{port}. Waiting for connections...")

    while True:
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr, server_username))
        client_handler.start()

if __name__ == "__main__":
    broadcast_port = 5001  # Port for broadcasting and listening for hosts
    main_port = 5000  # Main port for connections

    mode = input("Do you want to host or connect? (host/connect): ").strip().lower()
    if mode == "host":
        start_server(main_port)
    elif mode == "connect":
        print("Discovering hosts...")
        selected_host = listen_for_broadcasts(broadcast_port)
        if selected_host:
            connect_to_host(selected_host)
        else:
            print("No hosts found.")
    else:
        print("Invalid option. Please choose 'host' or 'connect'.")
