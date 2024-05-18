import socket
import threading
import random
import os
import json
import time

# Liste af adjektiver og substantiver til tilfældig brugernavngenerering
ADJECTIVES = ['Hurtig', 'Smuk', 'Glad', 'Rolig', 'Langsom']
NOUNS = ['Tiger', 'Hund', 'Kat', 'Haj', 'Ulv']

# Funktion til at generere et tilfældigt brugernavn
def generate_username():
    return random.choice(ADJECTIVES) + random.choice(NOUNS)

# Funktion til at udsende host oplysninger
def broadcast_host_details(broadcast_port, main_port, username):
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        host_details = {'username': username, 'ip': socket.gethostbyname(socket.gethostname()), 'port': main_port}
        message = json.dumps(host_details)
        broadcast_socket.sendto(message.encode('utf-8'), ('<broadcast>', broadcast_port))
        print(f"Broadcasting: {message}")
        time.sleep(2)  # Udsend hver 2. sekund

# Funktion til at lytte efter udsendelsesbeskeder
def listen_for_broadcasts(broadcast_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener_socket:
        listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener_socket.bind(('0.0.0.0', broadcast_port))
        listener_socket.settimeout(10)  # Timeout efter 10 sekunder

        try:
            while True:
                data, _ = listener_socket.recvfrom(1024)
                message = json.loads(data.decode('utf-8'))
                ip, username, port = message['ip'], message['username'], message['port']
                print(f"Received broadcast: {message}\nAvailable host: {username} at {ip}:{port}")
                choice = input("Do you want to connect to this host? (yes/no): ").strip().lower()
                if choice == "yes":
                    return message  # Returner den valgte host
                else:
                    continue  # Fortsæt med at lytte efter flere hosts
        except socket.timeout:
            pass

    return None  # Returner None hvis ingen hosts blev valgt

# Funktion til at oprette forbindelse til en host
def connect_to_host(host):
    host_ip, port = host['ip'], host['port']

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host_ip, port))

    # Generer og send klientens brugernavn
    client_username = generate_username()
    client.send(client_username.encode('utf-8'))

    # Modtag og vis serverens brugernavn
    server_username = client.recv(1024).decode('utf-8')
    print(f"Connected to host. Your username: {client_username}, Host's username: {server_username}")

    while True:
        file_name = input("Enter the name of the .txt file to request: ")
        client.send(file_name.encode('utf-8'))

        response = client.recv(1024).decode('utf-8')
        if response == "FILE_FOUND":
            with open(f"received_{file_name}", 'wb') as f:
                f.write(client.recv(4096))  # Juster bufferstørrelsen efter behov
            print(f"File '{file_name}' received and saved as 'received_{file_name}'.")
        else:
            print(f"File '{file_name}' not found on the host.")

# Funktion til at håndtere klientforbindelse og filoverførsel
def handle_client(client_socket, address, server_username):
    print(f"[+] {address} connected.")
    client_username = client_socket.recv(1024).decode('utf-8')
    client_socket.send(server_username.encode('utf-8'))
    print(f"Client's username: {client_username}")

    while True:
        try:
            # Modtag filanmodning
            file_name = client_socket.recv(1024).decode('utf-8')
            if not file_name:
                break

            if os.path.exists(file_name):
                client_socket.send("FILE_FOUND".encode('utf-8'))
                with open(file_name, 'rb') as f:
                    client_socket.send(f.read())
                print(f"File '{file_name}' sent to {client_username} at {address}.")
            else:
                client_socket.send("FILE_NOT_FOUND".encode('utf-8'))
                print(f"File '{file_name}' not found for {client_username} at {address}.")

        except ConnectionResetError:
            break

    print(f"[-] {address} disconnected.")
    client_socket.close()

# Funktion til at starte serveren
def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)

    # Generer og vis serverens brugernavn
    server_username = generate_username()
    print(f"Server's username: {server_username}")

    # Start udsendelse af host oplysninger
    broadcast_thread = threading.Thread(target=broadcast_host_details, args=(5001, port, server_username))
    broadcast_thread.start()
    print("Broadcasting host details...")

    # Hent og vis den lokale IP-adresse
    local_ip = socket.gethostbyname(socket.gethostname())
    print(f"[+] Server started on {local_ip}:{port}. Waiting for connections...")

    while True:
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr, server_username))
        client_handler.start()

if __name__ == "__main__":
    broadcast_port, main_port = 5001, 5000

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
