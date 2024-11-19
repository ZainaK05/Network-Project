#socket connection
import os
import socket
import threading
import sys

#file transfer
import tqdm
SEPARATOR = "<SEPARATOR>"
fsend = False
def upload_clicked():
    fsend = True
#user interface
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

#file upload frame
root = tk.Tk()
root.geometry("300x150")
root.resizable(False, False)
root.title('File uploader')

filename = tk.StringVar()

file = ttk.Frame(root)
file.pack(padx=10, pady=10, fill='x', expand=True)

up_file = ttk.Label(file, text="Type the name of the file below:")
up_file.pack(fill='x', expand=True)

upfile_entry = ttk.Entry(file, textvariable=filename)
upfile_entry.pack(fill='x', expand=True)
upfile_entry.focus()

upload_button = ttk.Button(file, text="Upload", command=upload_clicked)
upload_button.pack(fill='x', expand=True, pady=10)

root.mainloop()



#how to find the local ip of your device
#OSX/Linux: ifconfig
#Windows: ipconfig /all
# IP = "192.168.1.101" #"localhost"
IP = socket.gethostbyname("127.0.0.1")
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024 ## byte .. buffer size
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"



def main():


    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDR)
    while True:  ### multiple communications
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")

        if fsend:
            filesize = os.path.getsize(filename)
            client.send(f"{filename}{SEPARATOR}{filesize}".encode())
            fsend = False
            progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(filename, "rb") as f:
                while True:
                    # read the bytes from the file
                    bytes_read = f.read(SIZE)
                    if not bytes_read:
                        # file transmitting is done
                        break
                    # we use sendall to assure transimission in
                    # busy networks
                    client.sendall(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))

        if cmd == "OK":
            print(f"{msg}")
        elif cmd == "DISCONNECTED":
            print(f"{msg}")
            break
        
        data = input("> ") 
        data = data.split(" ")
        cmd = data[0]

        if cmd == "TASK":
            client.send(cmd.encode(FORMAT))

        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break
      



    print("Disconnected from the server.")
    client.close() ## close the connection

if __name__ == "__main__":
    main()

