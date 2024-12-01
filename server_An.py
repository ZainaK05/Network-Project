# Server Structure

# This is a multithreaded server used to handle multiple client
# connections simultaneously.

# It has data structures to manage files and client information.
# Logical file naming conventions to identify file types/avoid duplicate
# file names.
# It implements file transfer logic.
# It can handle authentication and authorization requests.
# It does not use FTP.

# Header files
import socket
import threading
import os
from cryptography.fernet import Fernet # Used for authentication
import pickle
import time

serverData = {
    "EndTime": 0,
    "FileSize": 0,
    "DownloadStart": 0,
    "DownloadEnd": 0,
}



# Generate key for authentication
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Socket connection
IP = "localhost"
PORT = 4493
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"
FILE_STORAGE_PATH = './server_files' # For file storage

# Authentication username/password
USER_CREDENTIALS = {
    "user1": "password1",
    "user2": "password2",
}

# File size limits (in bytes)
MAX_TEXT_SIZE = 25 * 1024 * 1024  # 25 MB
MAX_AUDIO_SIZE = 1 * 1024 * 1024 * 1024  # 1 GB
MAX_VIDEO_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB

# Function to check file type and size constraints
def validate_file_type_and_size(filename, file_size):
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        if file_size > MAX_TEXT_SIZE:
            return False, f"Text files must be smaller than 25 MB. The file size is {file_size / (1024 * 1024)} MB."
    elif ext == ".mp3" or ext == ".wav" or ext == ".flac":
        if file_size > MAX_AUDIO_SIZE:
            return False, f"Audio files must be smaller than 1 GB. The file size is {file_size / (1024 * 1024 * 1024)} GB."
    elif ext == ".mp4" or ext == ".mkv" or ext == ".avi":
        if file_size > MAX_VIDEO_SIZE:
            return False, f"Video files must be smaller than 2 GB. The file size is {file_size / (1024 * 1024 * 1024)} GB."
    else:
        return False, "Unsupported file type."

    return True, ""


# Function to authenticate users if the username and password match
def authenticate(username, password):
    return USER_CREDENTIALS.get(username) == password

# Function to handle the interactions with the client
def handle_client(client_socket, client_address):
    print(f"Connected to {client_address}")
    try:
        # Authentication
        client_socket.send(b"Enter username: ")
        username = client_socket.recv(1024).decode('utf-8').strip()
        client_socket.send(b"Enter password: ")
        password = client_socket.recv(1024).decode('utf-8').strip()

        # Authentication failure
        if not authenticate(username, password):
            client_socket.send(b"Authentication failed!\n")
            return

        # Authentication success
        client_socket.send(b"Authentication successful!\n")
        serverData["EndTime"] = time.time()
        with open("serverData.pickle", "wb") as outfile:
            pickle.dump(serverData, outfile)

        # Commands: UPLOAD, DOWNLOAD, DIR, DELETE, SUBFOLDER, EXIT
        while True:
            client_socket.send(b"Enter command (upload, download, dir, delete, subfolder, exit): ")
            command = client_socket.recv(1024).decode('utf-8').strip()

            if command == "UPLOAD":
                handle_upload(client_socket)
            elif command == "DOWNLOAD":
                handle_download(client_socket)
            elif command == "DIR":
                handle_list_files(client_socket)
            elif command == "DELETE":
                handle_delete(client_socket)
            elif command == "SUBFOLDER":
                handle_subfolder(client_socket)
            elif command == "EXIT":
                break
            else:
                client_socket.send(b"Unknown command!\n") # If user types in unknown command
    except Exception as e: # Error handling
        print(f"Error with client {client_address}: {e}")
    finally:
        client_socket.close() # Close the socket

# Function to handle uploading files
def handle_upload(client_socket):
    try:
        # Request file name from client
        client_socket.send(b"Enter file name to upload: ")
        filename = client_socket.recv(1024).decode('utf-8').strip()
        filepath = os.path.join(FILE_STORAGE_PATH, filename)

        # Request file size from client
        client_socket.send(b"Send file size: ")
        file_size = int(client_socket.recv(1024).decode('utf-8'))

        # Validate file type and size
        is_valid, validation_message = validate_file_type_and_size(filename, file_size)
        if not is_valid:
            client_socket.send(validation_message.encode('utf-8'))
            return

        # Check if file already exists and rename it to avoid conflicts
        if os.path.exists(filepath):
            client_socket.send(b"File with this name already exists, renaming...\n")
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filepath):
                new_filename = f"{base}_{counter}{ext}"
                filepath = os.path.join(FILE_STORAGE_PATH, new_filename)
                counter += 1
            filename = os.path.basename(filepath)  # Use new filename after renaming

        client_socket.send(b"Ready to receive file...\n")

        # Create directory if it doesn't exist
        if not os.path.exists(FILE_STORAGE_PATH):
            os.makedirs(FILE_STORAGE_PATH)

        # Receive file data and write it to the specified file path
        with open(filepath, 'wb') as f:
            bytes_received = 0
            while bytes_received < file_size:
                data = client_socket.recv(1024)
                if not data:
                    break
                bytes_received += len(data)
                f.write(data)
            serverData["UploadEnd"] = time.time()

        # If successful, show success message
        if bytes_received == file_size:
            client_socket.send(b"File uploaded successfully.\n")
        else:  # Error handling
            client_socket.send(b"File upload incomplete. Please try again.\n")
    except Exception as e:
        client_socket.send(f"Upload failed: {e}".encode('utf-8'))


# Function to handle downloading files ??? Kind of bugged
def handle_download(client_socket):
    try:
        # Enter file name you want to download
        client_socket.send(b"Enter file name to download: ")
        filename = client_socket.recv(1024).decode('utf-8').strip()
        filepath = os.path.join(FILE_STORAGE_PATH, filename)

        # If the file doesn't exist, show an error
        if not os.path.exists(filepath):
            client_socket.send(b"File not found!\n")
            return

        # Send file size
        file_size = os.path.getsize(filepath)
        serverData["FileSize"] = file_size
        client_socket.send(f"{file_size}".encode('utf-8'))

        # Send the file content
        serverData["DownloadStart"] = time.time()
        with open(filepath, 'rb') as f:
            while chunk := f.read(1024):
                client_socket.send(chunk)
            serverData["DownloadEnd"] = time.time()
        client_socket.send(b"File downloaded successfully.\n")
    except Exception as e:
        client_socket.send(f"Download failed: {e}".encode('utf-8'))


# Function to list the files uploaded in the directory
def handle_list_files(client_socket):
    try:
        files = os.listdir(FILE_STORAGE_PATH)
        if not files:
            client_socket.send(b"No files available.\n")
        else:
            client_socket.send("\n".join(files).encode('utf-8') + b"\n")
    except Exception as e:
        client_socket.send(f"Failed to list files: {e}".encode('utf-8'))


# Function to handle file deletion
def handle_delete(client_socket):
    try:
        client_socket.send(b"Enter file name to delete: ")
        filename = client_socket.recv(1024).decode('utf-8').strip()
        filepath = os.path.join(FILE_STORAGE_PATH, filename)

        if not os.path.exists(filepath):
            client_socket.send(b"File not found!\n")
            return

        os.remove(filepath)
        client_socket.send(b"File deleted successfully.\n")
    except Exception as e:
        client_socket.send(f"Deletion failed: {e}".encode('utf-8'))

# File to create or delete subfolders
def handle_subfolder(client_socket):
    try:
        client_socket.send(b"Enter command (create/delete) and folder name: ")
        command_and_folder = client_socket.recv(1024).decode('utf-8').strip()
        command, folder_name = command_and_folder.split()

        folder_path = os.path.join(FILE_STORAGE_PATH, folder_name)
        if command == 'create':
            os.makedirs(folder_path, exist_ok=True)
            client_socket.send(b"Subfolder created.\n")
        elif command == 'delete':
            if os.path.exists(folder_path):
                os.rmdir(folder_path)
                client_socket.send(b"Subfolder deleted.\n")
            else:
                client_socket.send(b"Subfolder not found.\n")
        else:
            client_socket.send(b"Invalid command.\n")
    except Exception as e:
        client_socket.send(f"Failed to manage subfolder: {e}".encode('utf-8'))

# Start the server!
def start_server():
    if not os.path.exists(FILE_STORAGE_PATH):
        os.makedirs(FILE_STORAGE_PATH)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(5)
    print(f"Server listening on {IP}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()


if __name__ == "__main__":
    start_server()
