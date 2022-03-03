from multiprocessing import connection
import socket
import traceback
from threading import Thread

from cgitb import reset
from rich import print
from rich.prompt import Prompt
from rich.table import Table

from champlistloader import load_some_champs
from core import Champion, Match, Shape, Team



def serverStart():
    start_server()


def start_server():
    host = "127.0.0.1"
    port = 5550   

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")

    try:
        soc.bind((host, port))
    except:
        print("Bind failed.")

    soc.listen(5)
    print("Socket now listening")

    
    while True:
        connection, address = soc.accept()
        ip, port = str(address[0]), str(address[1])
        print("Connected with " + ip + ":" + port)

        try:
            Thread(target=client_thread, args=(connection, ip, port)).start()
        except:
            print("Thread did not start.")
            traceback.print_exc()
            soc.close()


def client_thread(connection, ip, port, max_buffer_size = 1024):

    while True:
        client_input = get_input(connection, max_buffer_size)

        if client_input == "n":
            print("Client avslutter")
            connection.close()
            print("Connection " + ip + ":" + port + " closed")
            break


def get_input(connection, max_buffer_size):
    client_input = connection.recv(max_buffer_size)
    decoded_input = client_input.decode("utf8")
    result = print_input(decoded_input)
    return result


def print_input(input_str):
    return str(input_str).upper()

if __name__ == "__main__":
    serverStart()