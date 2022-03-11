from rich import print
import socket

DatabaseSocket = socket.socket() #database socket
DBhost = "127.0.0.1"
DBport = 6789
DatabaseSocket.bind((DBhost,DBport)) #binds to host and port
print("Database started")
print("Database is waiting for connection")
DatabaseSocket.listen(1) #listens for server

def start_database(): #starts database
    server, address = DatabaseSocket.accept()
    print("Connection established with: " + address[0] + ":" + str(address[1]))
    send_champions(server) #sends champions
    result = server.recv(4096).decode() #recieves and decodes the result
    if result:
        write_game(result)
        print("Game saved in file")
    else:
        print("No game was finished")

def write_game(result):
    x = open("game.txt", 'a') #opens game histort file, with a so it adds it on
    x.write(result) #writes result
    x.write("\n") #new line for next time
    x.close #closes file

#taken from champlistloader, edited so its a string
def from_csv(filename: str):
    champions = ""
    with open(filename, 'r') as f:  #opens file as read
        for line in f.readlines(): 
            champions += line #adds on a new line with champions
    return champions
#takes the server and sends champions
def send_champions(server):
    data = from_csv('some_champs.txt')
    server.send(data.encode())
#starts database 
if __name__ == "__main__":
    start_database()
