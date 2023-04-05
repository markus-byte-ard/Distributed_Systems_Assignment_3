###################################################################################################################################################################
# CT30A3401 Distributed Systems
# Author: Markus Taulu
# Date: 03.04.2023
# Sources: https://www.neuralnine.com/tcp-chat-in-python/ (basic structure)
# https://github.com/kevincobain2000/python-socket-chat/blob/6828093191d502f9ff27c628760fdc2f9bfbac6b/chat/server.py#L14 (idea for using dictionaries for rooms)
#
# server.py 
###################################################################################################################################################################

import socket
import threading
from time import sleep

## Connection Data
host = '127.0.0.1'
port = 55555

## Starting Server
## AF_INET is address family: IPv4 and SOCK_STREAM is the socket type: default TCP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

## Initialize Lists For Clients, Nicknames and commands and rooms dictionary with roomnames and clients in them
clients = []
nicknames = []
rooms = {}
rooms["main"] = {}
rooms["main"]["clients"] = []
commands = ["!help - list all commands", "!quit - Exit the chat application\n", "!pv@ <Username> - Send a private message to <Username>\n", 
            "!rooms - print available rooms and clients\n", "!addRoom <Roomname> - Create a new room with <Roomname>\n", 
            "!joinRoom <Roomname> - Join room with <Roomname>"]

## Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)
## End of def broadcast()

## Sending Messages To All Connected Clients in the senders room
def broadcastInRoom(message, user):
    for i in rooms:
        ## Searches what room the sender is in
        if user in rooms[i]["clients"]:
            ## Sends message to clients in the room
            for person in rooms[i]["clients"]:
                index = nicknames.index(person)
                clients[index].send(message)
## End of def broadcastInRoom()

## Print available rooms and clients in them
def broadcastRooms(nickname):
    index = nicknames.index(nickname)
    clients[index].send(str(rooms).encode())
## End of def broadcastRooms

## Print available commands to client
def broadcastCommands(nickname):
    index = nicknames.index(nickname)
    for command in commands:
        clients[index].send(str(command).encode())
## End of def broadcastCommands()

## Sending private Messages To one Client
def privateBroadcast(message, recipient):
    index = nicknames.index(recipient)
    clients[index].send(message)
## End of def privateBroadcast()

## Creating a new room
def addRooms(roomname):
    ## Check if room already exists
    if roomname in rooms:
        i = 0
        duplicate = True

        while (duplicate == True):
            i = i + 1

            if roomname + "_{}".format(i) not in rooms:
                roomname = roomname + "_{}".format(i)
                duplicate = False
                
    ## Create the new room
    rooms[roomname] = {}
    rooms[roomname]["clients"] = []
## End of def addRooms()

## Joining a new room if it exists
def joinRooms(roomname, user):
    if roomname in rooms:
        for i in rooms:
        ## Searches what room the sender is in
            if user in rooms[i]["clients"]:
                rooms[i]["clients"].remove(user)
                break
        rooms[roomname]["clients"].append(user)
    else:
        privateBroadcast("Room not available please create the room using command !addRoom <roomname>".encode(), user)
## End of def joinRooms()

## Handling Messages From Clients
def handle(client):
    while True:
        try:
            ## Broadcasting Messages
            index = clients.index(client)
            nickname = nicknames[index]
            message = client.recv(1024).decode()

            ## Private message if the message has the command
            if (message.find("!pv@") != -1):
                ## Split the message into a list and remove the command
                message = message.split()
                message.remove("!pv@")
                
                ## If the first word is a valid user, message is sent to the desired user
                ## Else a message is sent back to sender as an error message
                try:
                    index = nicknames.index(message[0])
                    receiver = nicknames[index]
                    ## Remove recipient name from message so that only the message is left
                    message.remove(receiver)
                    message = " ".join(message)
                    privateBroadcast("Private message from {}: {}".format(nickname, message).encode(), receiver)  
                except ValueError:
                    index = clients.index(client)
                    message = "Recipient does not exist"
                    receiver = nicknames[index]
                    privateBroadcast("Error message for {}: {}".format(nickname, message).encode(), receiver)                  
            
            ## if message is !rooms, prints available rooms to user 
            ## could also use find as above, but decided to use this method for both !rooms and !help
            elif (message == "!rooms"):
                broadcastRooms(nickname)

            ## if message is !help, prints available commands to user
            elif (message == "!help"):
                broadcastCommands(nickname)

            ## create a new room if the message has the command
            elif (message.find("!addRoom") != -1):
                message = message.split()
                ## Remove command from string
                message.remove("!addRoom")
                message = " ".join(message)
                addRooms(message)

            ## join a room if the message has the command
            elif (message.find("!joinRoom") != -1):
                message = message.split()
                ## Remove command from string
                message.remove("!joinRoom")
                message = " ".join(message)
                joinRooms(message, nickname)

            else:
                ## Sends message to all clients in the senders room
                ## broadcast("{}: {}".format(nickname, message).encode()) ## for debugging sends message to all clients regardless of room
                broadcastInRoom("{}: {}".format(nickname, message).encode(), nickname)

        except:
            ## Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]

            ## Remove user from the rooms dictionary
            for i in rooms:
                try:
                    rooms[i]["clients"].remove(nickname)
                    break
                except ValueError:
                    pass      
            
            broadcast('{} left!'.format(nickname).encode())
            nicknames.remove(nickname)
            break
## End of def handle()

## Receiving / Listening Function
def receive():
    while True:
        ## Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        ## Request And Store Nickname
        client.send('NICK'.encode())
        nickname = client.recv(1024).decode()

        ## Check if nickname already exists, increase number until is not a duplicate 
        ## this way if there are lets say user, user 1 and user 2, will create user 3
        if nickname in nicknames:
            i = 0
            duplicate = True

            while (duplicate == True):
                i = i + 1

                if nickname + "_{}".format(i) not in nicknames:
                    nickname = nickname + "_{}".format(i)
                    duplicate = False

        nicknames.append(nickname)
        clients.append(client)
        
        ## Add user to main room
        rooms["main"]["clients"].append(nickname)
        ##sleep(5)

        ## Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        broadcast("{} joined! ".format(nickname).encode())
        client.send('Connected to server!'.encode())

        ## Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
## End of def receive()

receive()

## EoF