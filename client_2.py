
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
filename = "25MB.bin"
filesize = os.path.getsize(filename)

def main():
    
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDR)

    client.send(f"{filename}{SEPARATOR}{filesize}".encode())
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(SIZE)
            if not bytes_read:
                break
            client.sendall(bytes_read)
            progress.update(len(bytes_read))




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

