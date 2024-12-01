# Client Structure

# Header Files
import socket
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.simpledialog import askstring
import threading
import pickle
import time

# Socket connection
SERVER_IP = '127.0.0.1'
SERVER_PORT = 4493

clientData = {
    "StartTime": 0,
    "FileSize": 0,
    "UploadStart": 0,
    "UploadEnd": 0,
}



# GUI
class FileSharingClient(tk.Tk):
    def __init__(self):
        super().__init__()

        # GUI size etc
        self.title("File Sharing Client")
        self.geometry("400x300")

        self.username = ""
        self.password = ""
        self.client_socket = None

        self.create_widgets()

    # Create gui widget
    def create_widgets(self):

        # To enter username
        self.username_label = tk.Label(self, text="Username")
        self.username_label.pack(pady=5)

        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        # To enter password
        self.password_label = tk.Label(self, text="Password")
        self.password_label.pack(pady=5)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        # Buttons for project requiremens
        self.login_button = tk.Button(self, text="Login", command=self.login)
        self.login_button.pack(pady=10)

        self.operation_label = tk.Label(self, text="Choose Operation")
        self.operation_label.pack(pady=5)

        self.upload_button = tk.Button(self, text="Upload File", command=self.upload_file, state=tk.DISABLED)
        self.upload_button.pack(pady=5)

        self.download_button = tk.Button(self, text="Download File", command=self.download_file, state=tk.DISABLED)
        self.download_button.pack(pady=5)

        self.dir_button = tk.Button(self, text="Directories", command=self.list_files, state=tk.DISABLED)
        self.dir_button.pack(pady=5)

        self.subfolder_button = tk.Button(self, text="Create Subfolder", command=self.subfolder_files, state=tk.DISABLED)
        self.subfolder_button.pack(pady=5)

        self.quit_button = tk.Button(self, text="Quit", command=self.quit)
        self.quit_button.pack(pady=5)

    # Login button, authenticates username and password to allow access to other buttons
    def login(self):
        """Login user and authenticate with server"""
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()

        if not self.username or not self.password:
            messagebox.showerror("Login Failed", "Please provide both username and password.")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientData["StartTime"] = time.time()
            self.client_socket.connect((SERVER_IP, SERVER_PORT))

            # Wait for server prompt for username
            server_message = self.client_socket.recv(1024).decode('utf-8')
            print(server_message)
            if "Enter username:" in server_message:
                self.client_socket.send(self.username.encode('utf-8'))

            # Wait for server prompt for password
            server_message = self.client_socket.recv(1024).decode('utf-8')
            print(server_message)
            if "Enter password:" in server_message:
                self.client_socket.send(self.password.encode('utf-8'))

            # Authenticate
            response = self.client_socket.recv(1024).decode('utf-8')
            print(response)
            if "Authentication successful" in response:
                messagebox.showinfo("Login Successful", "Authentication successful!")
                self.enable_operations()
            else: # Error handling
                messagebox.showerror("Login Failed", response)
        except Exception as e: # Error handling
            messagebox.showerror("Connection Error", str(e))

    # Now enable buttons after successful login! Uses state = normal
    def enable_operations(self):
        self.upload_button.config(state=tk.NORMAL)
        self.download_button.config(state=tk.NORMAL)
        self.dir_button.config(state=tk.NORMAL)
        self.subfolder_button.config(state=tk.NORMAL)
        self.quit_button.config(state=tk.NORMAL)

    # Logic for uploading files
    def upload_file(self):
        # Prompt
        file_path = filedialog.askopenfilename(title="Please select a file to upload.")

        # Error handling
        if not file_path:
            return

        # Logic
        try:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            clientData["FileSize"] = file_size

            # Send filename and size to the server
            self.client_socket.send(filename.encode('utf-8'))
            self.client_socket.send(str(file_size).encode('utf-8'))

            # Send the file in chunks
            clientData["UploadStart"] = time.time()
            with open(file_path, 'rb') as file:
                self.client_socket.send(file.read())
                clientData["UploadEnd"] = time.time()
            messagebox.showinfo("File Upload", "File uploaded successfully!")
            print(f"File '{filename}' was uploaded successfully to the server!")
        except Exception as e:
            messagebox.showerror("Upload Failed", str(e))
            print(f"File '{filename}' was not uploaded successfully to the server.")


    # Logic to download the file
    def download_file(self):
        filename = askstring("Download File", "Enter the filename to download:")
        if not filename:
            return
        try:
            # Send filename to server to request download
            print(f"Sending filename to server: {filename}")  # Debug log
            self.client_socket.send(filename.encode('utf-8'))

            # Receive file size from server
            file_size_str = self.client_socket.recv(1024).decode('utf-8')
            print(f"Server response for file size: {file_size_str}")  # Debug log

            try:
                file_size = int(file_size_str)
            except ValueError:
                raise ValueError("Invalid file size received from server.")

            if file_size == 0:
                messagebox.showerror("File Not Found", "File not found on the server.")
                return

            save_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=filename)
            if not save_path:
                return

            # Receive and save the file
            with open(save_path, 'wb') as file:
                bytes_received = 0
                while bytes_received < file_size:
                    data = self.client_socket.recv(1024)
                    if not data:
                        raise ConnectionError("Connection closed by server.")
                    bytes_received += len(data)
                    file.write(data)
                print(f"Received {bytes_received}/{file_size} bytes.")  # Debug log
            messagebox.showinfo("File Download", f"File {filename} downloaded successfully!")
            print(f"File '{filename}' was downloaded successfully to the server!")

        except Exception as e:
            messagebox.showerror("Download Failed", str(e))
            print(f"File '{filename}' was not downloaded successfully to the server.")


    # Logic to list file directories
    def list_files(self):
        try:
            self.client_socket.send(b"list")
            response = self.client_socket.recv(1024).decode('utf-8')
            files = response.split('\n')
            files = [f for f in files if f]  # Filter out empty entries

            if files:
                file_list = "\n".join(files)
                messagebox.showinfo("Files on Server", f"Available files:\n{file_list}")
            else:
                messagebox.showinfo("No Files", "No files uploaded.")
        except Exception as e:
            messagebox.showerror("List Files Failed", str(e))

    # Logic to create subfolder
    def subfolder_files(self):
        folder_name = askstring("Create Subfolder", "Enter the subfolder name:")
        if not folder_name:
            return

        try:
            # Send the command to the server to create the folder
            self.client_socket.send(f"create_subfolder@{folder_name}".encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')

            if "Subfolder created" in response:
                messagebox.showinfo("Success", f"Subfolder '{folder_name}' created successfully!")
            else:
                messagebox.showerror("Failed", f"Failed to create subfolder '{folder_name}'")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# Run
if __name__ == "__main__":
    client_app = FileSharingClient()
    client_app.mainloop()
    with open("clientData.pickle", "wb") as outfile:
        pickle.dump(clientData, outfile)