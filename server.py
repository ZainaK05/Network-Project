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

### Data structures for managing metadata (I'm not entirely sure about this one)
# Data structures
file_metadata = {} # For file metadata
client_metadata = {} # For client metadata

# Function to manage client information
def add_clients(addr, conn):
    client_metadata[addr] = conn
    print(f"[CONNECTED CLIENTS] {client_metadata.keys()}")

# Function to manage file information
def add_file_metadata(filename, file_type, file_size):
    file_id = generate_file_id(file_type) # Create a unique file ID
    file_metadata[file_id] = {"name": filename, "type": file_type, "size": file_size}
    print(f"{filename} stored as {file_id}")

# Create a unique ID based on the file type
def generate_file_id(file_type):
        prefix = {"text": "TXT", "audio": "AUD", "video": "VID"}.get(file_type, "GEN")
        return f"{prefix}{len(file_metadata) + 1:03}"

### File Naming Conventions
# Save the file
def save_file(file_type, filename, file_data):
    file_id = generate_file_id(file_type) # Create a file ID
    filepath = os.path.join(SERVER_PATH, file_id + "_" + filename)

    # Error handling to avoid duplicate files
    if os.path.exists(filepath):
        print("File Already Exists.")
        return False
    with open(filepath, "wb") as f:
        f.write(file_data)
    return True

### File Transfer Logic
# Upload Files
def file_upload(conn, filename, file_size):
    filepath = os.path.join(SERVER_PATH, filename) # File path
    with open(filepath, "wb") as f:
        bytes_received = 0
        while bytes_received < file_size: # Ensure the file is uploaded
            data = conn.recv(SIZE)
            if not data:
                break
            f.write(data)
            bytes_received += len(data)
    conn.send(f"OK@(filename) successfully uploaded.".encode(FORMAT)) # Send OK

# Download Files
def file_download(conn, filename):
    filepath = os.path.join(SERVER_PATH, filename)
    if not os.path.exists(filepath): # If the file can't be found
        conn.send("ERROR@File not found.".encode(FORMAT)) # Send error
        return
    with open(filepath, "rb") as f:
        conn.send(f"OK{os.path.getsize(filepath)}.".encode(FORMAT))
        conn.sendfile(f) # Sends file in chunks

### Authentication and Authorization
# Create usernames and passwords
users = {"ZainaK": "password123", "user2": "password1234"}

# Authenticate user
def authenticate(conn):
    conn.send("AUTH@Please enter username: ".encode(FORMAT)) # Enter username
    username = conn.recv(SIZE).decode(FORMAT)
    conn.send("AUTH@Please enter password: ".encode(FORMAT)) # Enter password
    password = conn.recv(SIZE).decode(FORMAT)

    if users.get(username) == password: # Authenticate, if username and password match authenticate, if not give an error
        conn.send("OK@Authenticated".encode(FORMAT))
        return True
    else:
        conn.send("ERROR@Invalid username or password.".encode(FORMAT))
        return False

### To handle the clients
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


if __name__ == "__main__":
    main()
