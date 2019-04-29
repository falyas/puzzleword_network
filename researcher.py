#Author: Farah Alyasari, 2019 All Rights Reserved.

import socket
import sys
import random

#this is a nonblocking socket object for IPV4 and UDP communication
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.setblocking(0)
server_addr = '127.0.0.1'
server_port = 5558
server = (server_addr, server_port)
my_addr = '127.0.0.1'
my_port = 5592          #can be changed per user
recv_buff_size = 512
send_buff = ''
my_id = 'researcher'
to_id = 'player'

#connect the socket to the server to be able to send to the server
sock.connect((server_addr, server_port))

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

#function: check the puzzle word format
def OnlyLetters(puzzle_word):
    puzzle_word = str(puzzle_word)
    return puzzle_word.isalpha()

#function: check the puzzle word length
def LengthCheck(puzzle_word, min, max):
    puzzle_word = str(puzzle_word)
    if( min <= len(puzzle_word) <= max): return True
    else: return False

while True:
    user_input = input(" ")

    #case 1: client demands to exit the program gracefully
    if 'stop' in user_input.lower():
        #expected send_buff: client_id->server#<ip>{port}(offline)
        send_buff = my_id+'->'+server_addr + '{' + str(my_port) + '}' + '(offline)'
        sock.sendto(send_buff.encode(), server)
        break;

    #case 2: researcher is hosting the puzzle word game
    #expected user input: start
    elif 'start' in user_input.lower():
        #expected send_buff: client_id->server#<ip>{port}
        send_buff = my_id+'->'+server_addr + '{' + str(my_port) + '}'
        sock.sendto(send_buff.encode(), server)

        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
        print("Welcome to the UR5 puzzle game challenge, this is the researcher view! \n")
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
        print("The game rules are simple:\n")
        print("1 . Choose a puzzle word between 3 to 5 letters long\n")
        print("2 . Don't use numbers or special characters\n")
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
        puzzle_word = input("Please enter a puzzle word: ")
        data_check = ( OnlyLetters(puzzle_word) and LengthCheck(puzzle_word,3,5))
        print("\n")
        while (data_check == False):
            puzzle_word = input("\nPlease follow the game rules! Try another puzzle word: ")
            data_check = ( OnlyLetters(puzzle_word) and LengthCheck(puzzle_word,3,5))
            print("\n")
        message_id = random_int(10,1,9)
        message_id = str(message_id)
        #expected format: client_id_1->client_id_2#<msg_id:######>{[puzzle_word]:some_message}
        send_buff = my_id+'->'+to_id+"#<msg_id:"+message_id+">{[puzzle_word]:"+str(puzzle_word)+"}"
        sock.sendto(send_buff.encode(), server)

        #wait to recieve a confirmation from server that the message was forwarded successfully
        data, server = sock.recvfrom(recv_buff_size)
        data = data.decode()
        if('success' in data):
            print('puzzle word successfully forwarded to the player\n')
        #else: the to client is offline
        else:
            break

        print('... waiting for the player to guess the word ... \n')

        #game in process, some initial values
        guess_count = 1
        hint_count = 1
        guess = ''
        while puzzle_word.lower() != guess.lower():
            data, server = sock.recvfrom(recv_buff_size)
            data = data.decode()

            #expected format: from player:{[guess]:some message} or from player:{[hint]:help}
            if '[guess]' in data:
                guess = find_substring(data, ']:','}')
                guess_count = guess_count + 1
                print('('+ str(guess_count)+') The player guessed: ' + guess)

            elif '[hint]' in data:
                print("\n["+str(hint_count)+"] Player is requesting a hint!")
                hint = input("\nPlease keep your hint under 250 letters: ")
                hint_count = hint_count + 1
                hint_check = LengthCheck(hint, 0, 250)
                while (hint_check == False):
                    hint_check = input("\nSorry, hint must be under 250 letters: ")
                    hint_check = ( OnlyLetters(puzzle_word) and LengthCheck(hint_check,0,250))
                    print("\n")
                message_id = random_int(10,1,9)
                message_id = str(message_id)
                #expected format: client_id_1->client_id_2#<msg_id:######>{[hint]:some_message}
                send_buff = my_id+'->'+to_id+"#<msg_id:"+message_id+">{[hint]:"+str(hint)+"}"
                sock.sendto(send_buff.encode(), server)
            elif 'success' in data:
                print("\nhint successfully forwarded to player")
            else:
                print("\nunexpected message from the server")

        print("\nthe player guessed the word correctly")

    #case 3: user gives inputs other than stop and start
    else:
        print("\nEnter 'stop' to close the game and 'start' to begin the game")
