from rich import print
from core import Champion
import socket

DatabaseSocket = socket.socket()
DBhost = "127.0.0.1"
DBport = 6789
DatabaseSocket.bind((DBhost,DBport))
print("Database started")
print("Database is waiting for connection")
DatabaseSocket.listen(1)

def start_database():
    client, address = DatabaseSocket.accept()
    print("Connection established with: " + address[0] + ":" + str(address[1]))
    send_champions(client)
    result = client.recv(4096).decode()
    print("Match logged in database")
    x = open("game.txt", 'a')
    x.write(result)
    x.write("\n")
    x.close

def from_csv(filename: str) -> dict[str, Champion]:
    champions = ""
    with open(filename, 'r') as f:
        for line in f.readlines():
            champions += line
    return champions

def load_some_champs():
    return from_csv('some_champs.txt')

def send_champions(client):
    data = load_some_champs()
    client.send(data.encode())
start_database()