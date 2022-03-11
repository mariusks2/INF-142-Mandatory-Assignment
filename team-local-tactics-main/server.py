import socket
from rich import print
from _thread import *
import json
from core import Champion, Match, Shape, Team
from rich import print
from rich.table import Table

ServerSocket = socket.socket() #makes socket named ServerSocket
host = "127.0.0.1"
port = 5550
ServerSocket.bind((host, port))
print('Server is waiting for connections')
ServerSocket.listen(2) #listens for 2 clients

DBhost = "127.0.0.1"
DBport = 6789 #different port for DB
DB_socket = socket.socket() #makes socket named DB_socket
DB_socket.connect((DBhost, DBport))  #connect to the database

antall = 0 #antall connections
champions = [] #list of champions chosen
connections = [] #list of connections

def format_champions(champions) -> dict[str, Champion]: #taken from champlistloader
    champions_dict = {}
    for line in champions.split("\n"):
        champ = _parse_champ(line)
        champions_dict[champ.name] = champ
    return (champions_dict)

def _parse_champ(champ_text): #taken from champlistloader
    name, rock, paper, scissors = champ_text.split(sep=',')
    return Champion(name, float(rock), float(paper), float(scissors))
#taken from team_local_tactics
def print_match_summary(match: Match):
    EMOJI = {
        Shape.ROCK: ':raised_fist-emoji:',
        Shape.PAPER: ':raised_hand-emoji:',
        Shape.SCISSORS: ':victory_hand-emoji:'
    }

    #For each round print a table with the results
    for index, round in enumerate(match.rounds):

        #Create a table containing the results of the round
        round_summary = Table(title=f'Round {index+1}')

        #Add columns for each team
        round_summary.add_column("Red",
                                 style="red",
                                 no_wrap=True)
        round_summary.add_column("Blue",
                                 style="blue",
                                 no_wrap=True)

        #Populate the table
        for key in round:
            red, blue = key.split(', ')
            round_summary.add_row(f'{red} {EMOJI[round[key].red]}',
                                  f'{blue} {EMOJI[round[key].blue]}')
        print(round_summary)
        print('\n')

    #Print the score
    red_score, blue_score = match.score
    print(f'Red: {red_score}\n'
          f'Blue: {blue_score}')

    #Print the winner
    if red_score > blue_score:
        a = ('\n[red]Red victory! :grin:')
    elif red_score < blue_score:
        a = ('\n[blue]Blue victory! :grin:')
    else:
        a = ('\nDraw :expressionless:')
    return [a, red_score, blue_score]
#taken from team_local_tactics
def print_available_champs(champions: dict[Champion]) -> None:

    # Create a table containing available champions
    available_champs = Table(title='Available champions')

    # Add the columns Name, probability of rock, probability of paper and
    # probability of scissors
    available_champs.add_column("Name", style="cyan", no_wrap=True)
    available_champs.add_column("prob(:raised_fist-emoji:)", justify="center")
    available_champs.add_column("prob(:raised_hand-emoji:)", justify="center")
    available_champs.add_column("prob(:victory_hand-emoji:)", justify="center")

    # Populate the table
    for champion in champions.values():
        available_champs.add_row(*champion.str_tuple)
    return(available_champs)
#main, takes champions chosen
def main(a, b, c, d):
    print('\n'
          'Welcome to [bold yellow]Team Local Tactics[/bold yellow]!'
          '\n'
          'Each player choose a champion each time.'
          '\n')
    #takes champions from DB, formats
    champions = format_champions(championsDB)
    print_available_champs(champions)
    print('\n')
    #player1 has pick a,b
    player1 = [a,b]
    player2 = [c,d] #player2 has pick c,d

    print('\n')

   #Match
    match = Match(
        Team([champions[name] for name in player1]),
        Team([champions[name] for name in player2])
    )
    match.play()

    return (match)
#recievs champions from DB
championsDB = DB_socket.recv(4096).decode()

#sends champions to client
def champs(connection):
    connection.send(championsDB.encode())

#server plays the game
def server_game(connection):
    connection.send(str(antall).encode()) #sends connection number
    champs(connection) #runs champs
    while True:
        connections.append(connection) #list of each connection
        championsChosen = connection.recv(4096).decode()
        p1 = json.loads(championsChosen) #using json.loads to make it appendable below.
        champions.append(p1['P1']) #list with champions picked
        champions.append(p1['P2'])
        
        if len(connections) >=2: #if 2 or more connections send champions to client for comparison
            s1 = json.dumps(p1).encode()
            connections[1].send(s1)
        
        if len(champions)==4: #if all champions have been chosen
            result = print_match_summary(main(str(champions[0]), str(champions[1]),str(champions[2]), str(champions[3]))) #runs game with picked champions
            connections[0].send(result[0].encode()) #sends result from game to player1
            connections[1].send(result[0].encode()) #sends result from game to player2
            print(result[0]) #prints result in server
            
            result_dict={"Result": "","Red Score":"", "Blue Score":""} #dict to send to DB
            if result[0][3] == "e": #suffy method but works. rEd
                result_dict.update({"Result": "Red Victory"})
            elif result[0][3] == "l":#suffy method but works. bLue
                result_dict.update({"Result": "Blue Victory"})
            else:
                result_dict.update({"Result": "Draw"})
            result_dict.update({"Red Score": result[1]}) #red score
            result_dict.update({"Blue Score": result[2]}) #blue score
            data = json.dumps(result_dict).encode() #json to make it into json string
            DB_socket.send(data) #sends to DB




# Multithread
while True:
    client, address = ServerSocket.accept()
    print("Connection established with: " + address[0] + ":" + str(address[1]))
    start_new_thread(server_game, (client, ))
    antall += 1
    print('Connections: ' + str(antall))
