# Header files
import os
import socket
import threading

# Server port
IP = "localhost"
PORT = 4450
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"

# Data structures for managing data
clients = {}
file_metadata = {}

def add_clients(addr, conn):
    clients[addr] = conn
    print(f"[CONNECTED CLIENTS] {clients.keys()}")
def add_file_metadata(filename, file_type, file_size):
    file_id = generate_file_id(file_type)
    file_metadata[file_id] = {"name": filename, "type": file_type, "size": file_size}
    print(f"{filename} stored as {file_id}")

def generate_file_id(file_type):
        prefix = {"text": "TS", "audio": "AU", "video": "VI"}.get(file_type, "GEN")
        return f"{prefix}{len(file_metadata) + 1:03}"

# File Naming Conventions
def save_file(file_type, filename, file_data):
    file_id = generate_file_id(file_type)
    filepath = os.path.join(SERVER_PATH, file_id + "_" + filename)

    # Error handling - avoid duplicate files
    if os.path.exists(filepath):
        print("File Already Exists.")
        return False
    with open(filepath, "wb") as f:
        f.write(file_data)
    return True

# File Transfer Logic
def file_upload(conn, filename, file_size):
    filepath = os.path.join(SERVER_PATH, filename)
    with open(filepath, "wb") as f:
        bytes_received = 0
        while bytes_received < file_size:
            data = conn.recv(SIZE)
            if not data:
                break
            f.write(data)
            bytes_received += len(data)
    conn.send(f"OK@(filename) successfully uploaded.".encode(FORMAT))

def file_download(conn, filename):
    filepath = os.path.join(SERVER_PATH, filename)
    if not os.path.exists(filepath):
        conn.send("ERROR@File not found.".encode(FORMAT))
        return
    with open(filepath, "rb") as f:
        conn.send(f"OK{os.path.getsize(filepath)}.".encode(FORMAT))
        conn.sendfile(f) # Sends file in chunks

# Authentication and Authorization
users = {"user1": "password123", "user2": "password"}

def authenticate(conn):
    conn.send("AUTH@Please enter username: ".encode(FORMAT))
    username = conn.recv(SIZE).decode(FORMAT)
    conn.send("AUTH@Please enter password: ".encode(FORMAT))
    password = conn.recv(SIZE).decode(FORMAT)

    if users.get(username) == password:
        conn.send("OK@Authenticated".encode(FORMAT))
        return True
    else:
        conn.send("ERROR@Invalid username or password.".encode(FORMAT))
        return False

# To handle the clients
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the server".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]

        send_data = "OK@"

        if cmd == "LOGOUT":
            break

        # Upload File
        elif cmd == "UPLOAD":
            filename = data[1]
            filesize = int(data[2])
            filepath = os.path.join(SERVER_PATH, filename)

            with open(filepath, "wb") as f:
                bytes_read = conn.recv(SIZE)
                f.write(bytes_read)

            send_data +=f"File {filepath} has been uploaded!\n"
            conn.send(send_data.encode(FORMAT))

        elif cmd == "DOWNLOAD":
            filename = data[1]
            filepath = os.path.join(SERVER_PATH, filename)

            if os.path.exists(filepath):
                conn.send(f"EXISTS@{os.path.getsize(filepath)}".encode(FORMAT))
                with open(filepath, "rb") as f:
                    bytes_read = f.read(SIZE)
                    conn.sendall(bytes_read)
            else:
                conn.send("ERROR@File not found.".encode(FORMAT))

        elif cmd == "DELETE":
            filename = data[1]
            filepath = os.path.join(SERVER_PATH, filename)

            if os.path.exists(filepath):
                os.remove(filepath)
                send_data += f"File {filepath} has been deleted!\n"
            else:
                send_data = "ERROR@File not found.".encode(FORMAT)
            conn.send(send_data.encode(FORMAT))




        elif cmd == "TASK":
            send_data += "LOGOUT from the server.\n"

            conn.send(send_data.encode(FORMAT))

    print(f"{addr} disconnected")
    conn.close()


def main():
    print("Starting the server")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  ## used IPV4 and TCP connection
    server.bind(ADDR)  # bind the address
    server.listen()  ## start listening
    print(f"server is listening on {IP}: {PORT}")

    while True:
        conn, addr = server.accept()  ### accept a connection from a client
        # Multithreading
        thread = threading.Thread(target=handle_client, args=(conn, addr))  ## assigning a thread for each client
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


if __name__ == "__main__":
    main()
