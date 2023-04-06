###################################################################################################################################################################
# CT30A3401 Distributed Systems
# Author: Markus Taulu
# Date: 03.04.2023
# Sources: https://www.neuralnine.com/tcp-chat-in-python/ (basic structure)
#
# client.py
###################################################################################################################################################################

import socket
import threading
import sys

## Choosing a Nickname
nickname = input("Choose your nickname: ")
nickname = nickname.split()
nickname = "_".join(nickname)

## Connecting To Server 
address = input("Input server address: ")

## AF_INET is address family: IPv4 and SOCK_STREAM is the socket type: default TCP socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

## Timeout error takes a good amount of time to occur, but works
try:
    client.connect((address, 55555))
    ## client.connect(('127.0.0.1', 55555)) ## for faster debugging
except (TimeoutError, ConnectionRefusedError) as error:
    print("Connection failed")
    sys.exit()

## Listening to Server and Sending Nickname
def receive():
    while True:
        try:
            ## Receive Message From Server
            ## If 'NICK' Send Nickname
            message = client.recv(1024).decode()
            if message == 'NICK':
                client.send(nickname.encode())
            else:
                print(message)
        except:
            ## Close Connection When an Error occurs
            print("An error occurred!")
            client.close()
            break

## Sending Messages To Server
def write():
    while True:
        message = input('')

        if (message == "!quit"):
            client.close()
            sys.exit()
            ## Calls the receive exception and prints An error occurred, couldn't think of an easy way to stop this 
        else:
            ## Send message to server
            client.send(message.encode())

## Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

## EoF