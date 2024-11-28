import os
import socket
import threading
import sys

import tqdm


IP = "127.0.0.1"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

#filestoring protocol


#filesharing protocol
SEPARATOR = "<SEPARATOR>"
#place a filename from the directory here:

filename = "test.txt"
filesize = os.path.getsize(filename)

def main():
    
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDR)

    client.send(f"{filename}{SEPARATOR}{filesize}".encode())
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=SIZE)
    with open(filename, "rb") as f:
        while True:

            print("File size before open: ", os.path.getsize(filename))

            bytes_read = open(filename, "rb").read(SIZE)
            print("File size after open: ", os.path.getsize(filename))
            if not bytes_read:
                break
            client.sendall(bytes_read)
            print("File size after send: ", os.path.getsize(filename))
            progress.update(len(bytes_read))
            print("File size after progress.update: ", os.path.getsize(filename))





    while True:
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")
        if cmd == "OK":
            print(f"{msg}")
        elif cmd == "DISCONNECTED":
            print(f"{msg}")
            break
        
        data = input("> ") 
        data = data.split(" ")
        cmd = data[0]

        if cmd == "HELP":
            client.send(cmd.encode(FORMAT))
        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break


    print("Disconnected from the server.")
    client.close() ## close the connection

if __name__ == "__main__":
    main()

