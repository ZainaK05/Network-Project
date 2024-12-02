import tkinter as tk
import pickle
from pathlib import Path

client = Path("/clientData.pickle")
server = Path("/serverData.pickle")

if client.is_file() and server.is_file():
    with open("clientData.pickle", "rb") as infile:
        clientDict = pickle.load(infile)
    print(clientDict)

    with open("serverData.pickle", "rb") as infile:
        serverDict = pickle.load(infile)
    print(serverDict)

    responseTime = round((serverDict["EndTime"] - clientDict["StartTime"]) * 1000, 3)
    print(f"\nResponse Time: {responseTime} milliseconds")

    uploadTime = round((clientDict["UploadEnd"] - clientDict["UploadStart"]), 3)
    uploadRate = round(clientDict["FileSize"] / (clientDict["UploadEnd"] - clientDict["UploadStart"]), 1)
    print(f"Upload Time: {uploadTime} milliseconds")
    print(f"Upload Rate: {uploadRate} bytes per second")

    # downloadTime = (serverDict["DownloadEnd"] - serverDict["DownloadStart"])
    # downloadRate = serverDict["FileSize"] / downloadTime
    # print(downloadTime * 1000, "milliseconds")
    # print(downloadRate, "bytes per second")
else:
    print("You are missing data, please ensure you have the pickled files for both client and server")
