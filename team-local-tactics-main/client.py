import socket
from rich import print
from rich.table import Table
import json
from rich.prompt import Prompt
from core import Champion

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
    print(available_champs)
#taken from team_local_tactics
def input_champion(prompt: str,
                   color: str,
                   champions: dict[Champion],
                   player1: list[str],
                   player2: list[str]):

    # Prompt the player to choose a champion and provide the reason why
    # certain champion cannot be selected
    while True:
        match Prompt.ask(f'[{color}]{prompt}'):
            case name if name not in champions:
                print(f'The champion {name} is not available. Try again.')
            case name if name in player1:
                print(f'{name} is already in your team. Try again.')
            case name if name in player2:
                print(f'{name} is in the enemy team. Try again.')
            case _:
                player1.append(name)
                break
    return player1 
#taken from team_local_tactics. format_champions(champs) takes a string of champs, into format_champions()
def intro(champs):
    print('\n'
          'Welcome to [bold yellow]Team Local Tactics[/bold yellow]!'
          '\n'
          'Each player choose a champion each time.'
          '\n')

    champions = format_champions(champs)
    print_available_champs(champions)
    print('\n')
#runs the input for player1, red as color
def player1Game(num, listofchamps, champs):
    player1 = []
    champions = format_champions(champs)

    for i in range(2):
        player1 = input_champion('Player '+num, 'red', champions, player1, listofchamps)
    return player1
#runs the input for player2, blue as color
def player2Game(num, listofchamps, champs):
    player1 = []
    champions = format_champions(champs)

    for i in range(2):
        player1 = input_champion('Player '+num, 'blue', champions, player1, listofchamps)
    return player1
#takes a string of champions and turns it into a dict with _parse_champ
def format_champions(champions) -> dict[str, Champion]:
    champions_dict = {}
    for line in champions.split("\n"):
        champ = _parse_champ(line)
        champions_dict[champ.name] = champ
    return (champions_dict)
#takes string and makes it into a Champion
def _parse_champ(champ_text: str) -> Champion:
    name, rock, paper, scissors = champ_text.split(sep=',')
    return Champion(name, float(rock), float(paper), float(scissors))

#client start, acts as clients
def client_start():
    host = "127.0.0.1"  #localhost
    port = 5550  #port
    client_socket = socket.socket() #creates socket named client_socket
    client_socket.connect((host, port))  #connect to the server on localhost and port 5550
    while True:
        champion_pick = []  #list of champions chosen
        num = client_socket.recv(4096).decode() #recieves number
        champs = client_socket.recv(4096).decode() #recieves champs from server, that got them from database
        if (num == "1"): #if client is first, player 1
            intro(champs) #plays intro, takes champs which is string of all the champs
            print("Please select 2 champions")
            champion_pick = player1Game("1", champion_pick, champs) #uses player1 game to list the chosen champions
            print("Waiting for player 2 to send input")
            pickTuple1 = {"P1":champion_pick[0], "P2":champion_pick[1]} #tuple, chosen champions
            jsonTuple1 = json.dumps(pickTuple1).encode() #json encode to send a tuple. makes it a json string
            client_socket.send(jsonTuple1) #sends the json string
        elif (num == "2"): #if connection 2, player 2
            print("help")
            intro(champs) #plays intro, takes champs which is string of all the champs
            print("Waiting for player 1 to send input")
            p1 = client_socket.recv(4096).decode() #recieves what player 1 chose
            #print("Player 1 chose: "+ p1) unfair to show player 2 what player1 chose
            s1 = json.loads(p1) #using json.loads to make it appendable below.
            
            # List of player 1 champions
            player1Champs = []
            player1Champs.append(s1['P1'])
            player1Champs.append(s1['P2'])

            champion_pick = player2Game("2", player1Champs, champs) #if champion is in player1Champs, cant be chosen. process done in input_champion
            pickTuple2 = {"P1":champion_pick[0], "P2":champion_pick[1]}  #tuple for player 2
            jsonTuple2 = json.dumps(pickTuple2).encode() #json encode to send a tuple. makes it a json string
            client_socket.send(jsonTuple2) #sends the json string
            player2choice = client_socket.recv(4096).decode() #recieves what champions player2 chose
            
        result = client_socket.recv(4096).decode() #recieves result from server
        print(result) #prints result

if __name__ == "__main__":
    client_start()