#Author: Farah Alyasari, 2019 All Rights Reserved.

import socket
import sys
import random

#this is a nonblocking socket object for IPV4 and UDP communication
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.setblocking(0)
my_addr = '127.0.0.1'
my_port = 5578          #can be changed per user
server_client_addr = '127.0.0.1'
server_client_port = 5558
server = (server_client_addr, server_client_port)
recv_buff_size = 512
send_buff = ''
my_id = 'ubuntu'

#connect the socket to the server to be able to send to the server
sock.connect(server)

#function: use to extract information from the data recieved it will
#always extract the first and the last which show up earlier in the string
def find_substring( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        if(last == 'end_of_string'):
            end = len(s)
        else:
            end = s.index( last, start )
            return s[start:end]
    except ValueError:
        return 'error_s'

#function: generates a random number to send in the header of the datagram
def random_int(length,lowest,highest):
    string_of_ints = ''
    for x in range(length):
        string_of_ints += str( random.randint(lowest,highest))
    val = int(string_of_ints)
    return val

while True:
    user_input = input(" ")

    #case 1: client demands to exit the program gracefully
    if 'stop' in user_input.lower():
        break;

    #case 2: researcher is hosting the puzzle word game
    #expected user input: start
    elif 'start' in user_input.lower():

        #expected send_buff: client_id->server#<ip>{port}
        send_buff = my_id+'->'+server_client_addr + '{' + str(my_port) + '}'
        sock.sendto(send_buff.encode(), server)

        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n")
        print("Welcome to the UR5 puzzle game challenge,\n")
        print("this is the ubuntu view! \n")
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n")
        print("This client has two jobs:\n")
        print("1 . Recieve correct letters from the server\n")
        print("2 . Store the correct letters inside a file\n")
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n")

        while True:
            data, server_client_addr = sock.recvfrom(recv_buff_size)
            data = data.decode()
            letters = ''
            if ('letters' in data):
                #expected format: from player: {[letters]:some message}
                letters = find_substring(data, ']:','}')
                print("letters recieved: " + letters)
                #store letters in a file
                f=open("letters.txt","w+")
                f.write(letters)
                f.close()
                print("letters saved")
            else:
                print("no letters in data")
