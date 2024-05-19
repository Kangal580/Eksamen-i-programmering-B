import socket
import threading
import random
import os
import json
import time
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Liste af adjektiver og substantiver til tilfældig brugernavngenerering
ADJECTIVES = ['Hurtig', 'Smuk', 'Glad', 'Rolig', 'Langsom']
NOUNS = ['Tiger', 'Hund', 'Kat', 'Haj', 'Ulv']


# Funktion til at generere et tilfældigt brugernavn
def generate_username():
    return random.choice(ADJECTIVES) + random.choice(NOUNS)


# Funktion til at generere RSA-nøgler
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key


# Funktion til at serialisere offentlig nøgle
def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


# Funktion til at deserialisere offentlig nøgle
def deserialize_public_key(public_key_bytes):
    return serialization.load_pem_public_key(public_key_bytes)


# Funktion til at udsende host oplysninger
def broadcast_host_details(broadcast_port, main_port, username, public_key, public_key_bytes):
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        encrypted_username = public_key.encrypt(
            username.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # Encode encrypted_username bytes objekt til Base64 strings
        encrypted_username_base64 = base64.b64encode(encrypted_username).decode('utf-8')

        host_details = {
            'username': encrypted_username_base64,
            'ip': socket.gethostbyname(socket.gethostname()),
            'port': main_port,
            'public_key': public_key_bytes.decode('utf-8')
        }
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
                public_key = deserialize_public_key(message['public_key'].encode('utf-8'))
                print(f"Received broadcast: {message}\nAvailable host: {username} at {ip}:{port}")
                choice = input("Do you want to connect to this host? (yes/no): ").strip().lower()
                if choice == "yes":
                    return {'ip': ip, 'port': port, 'public_key': public_key}  # Returner den valgte host
                else:
                    continue  # Fortsæt med at lytte efter flere hosts
        except socket.timeout:
            pass

    return None  # Returner None hvis ingen hosts blev valgt


# Funktion til at oprette forbindelse til en host
def connect_to_host(host):
    host_ip, port, public_key = host['ip'], host['port'], host['public_key']

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host_ip, port))

    # Generate og send clients navn
    client_username = generate_username()
    print(f"Generated client's username: {client_username}")
    encrypted_username = public_key.encrypt(
        client_username.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print(f"Encrypted client's username: {encrypted_username}")
    client.send(encrypted_username)

    # Modtag og vis serverens navn
    server_username_encrypted = client.recv(256)
    server_username = server_username_encrypted.decode('utf-8')
    print(f"Connected to host. Your username: {client_username}, Host's username: {server_username}")

    while True:
        file_name = input("Enter the name of the .txt file to request: ")
        encrypted_file_name = public_key.encrypt(
            file_name.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print(f"Plaintext file name to request: {file_name}")
        print(f"Encrypted file name to request: {encrypted_file_name}")
        client.send(encrypted_file_name)

        response = client.recv(1024).decode('utf-8')
        if response == "FILE_FOUND":
            with open(f"received_{file_name}", 'wb') as f:
                f.write(client.recv(4096))  # Juster bufferstørrelsen efter behov
            print(f"File '{file_name}' received and saved as 'received_{file_name}'.")
        else:
            print(f"File '{file_name}' not found on the host.")


# Funktion til at håndtere klientforbindelse og filoverførsel
def handle_client(client_socket, address, server_username, private_key):
    print(f"[+] {address} connected.")
    encrypted_client_username = client_socket.recv(256)
    print(f"Encrypted client username received: {encrypted_client_username}")
    client_username = private_key.decrypt(
        encrypted_client_username,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode('utf-8')
    print(f"Decrypted client's username: {client_username}")
    client_socket.send(server_username.encode('utf-8'))

    while True:
        try:
            encrypted_file_name = client_socket.recv(256)
            print(f"Encrypted file name received: {encrypted_file_name}")
            file_name = private_key.decrypt(
                encrypted_file_name,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode('utf-8')
            print(f"Decrypted file name: {file_name}")

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

    # Generer RSA-nøgler
    private_key, public_key = generate_rsa_keys()
    public_key_bytes = serialize_public_key(public_key)

    # Generer og vis serverens brugernavn
    server_username = generate_username()
    print(f"Server's username: {server_username}")

    # Start udsendelse af host oplysninger
    broadcast_thread = threading.Thread(target=broadcast_host_details,
                                        args=(5001, port, server_username, public_key, public_key_bytes))
    broadcast_thread.start()
    print("Broadcasting host details...")

    # Hent og vis den lokale IP-adresse
    local_ip = socket.gethostbyname(socket.gethostname())
    print(f"[+] Server started on {local_ip}:{port}. Waiting for connections...")

    while True:
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client,
                                          args=(client_socket, addr, server_username, private_key))
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