#Author: Farah Alyasari, 2019 All Rights Reserved.

import socket
import sys
import random
from itertools import zip_longest

#this is a nonblocking socket object for IPV4 and UDP communication
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.setblocking(0)
server_addr = '127.0.0.1'
server_port = 5558
server = (server_addr, server_port)
my_addr = '127.0.0.1'
my_port = 5587          #can be changed per user
recv_buff_size = 512
send_buff = ''
my_id = 'player'
researcher_id = 'researcher'
ubuntu_id = 'ubuntu'

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
def OnlyLetters(word):
    word = str(word)
    return word.isalpha()

#function: check the puzzle word length
def LengthCheck(word):
    word = str(word)
    if word == '?': return True
    else:
        if( 3 <= len(word) <= 5): return True
        else: return False

#function: match letters of two strings, if letters do not match put "_"
def match_letters(puzzle_word, guess):
    correct_and_guess = [(puzzle_word, guess), (puzzle_word, guess)]
    for correct, guess in correct_and_guess:
        # If characters in same positions match, then show character, otherwise show `_`
        new_word = ''.join(c if c == g else '_' for c, g in zip_longest(correct, guess, fillvalue='_'))
    return new_word

while True:
    user_input = input(" ")

    #case 1: client demands to exit the program gracefully
    if 'stop' in user_input.lower():
        #expected send_buff: client_id->server#<ip>{port}(offline)
        send_buff = my_id+'->'+server_addr + '{' + str(my_port) + '}' + '(offline)'
        sock.sendto(send_buff.encode(), server)
        break;

    #case 2: player is doing the puzzle word game
    #expected user input: start
    elif 'start' in user_input.lower():
        #expected send_buff: client_id->server#<ip>{port}
        send_buff = my_id+'->'+server_addr + '{' + str(my_port) + '}'
        sock.sendto(send_buff.encode(), server)
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
        print("Welcome to the UR5 puzzle game challenge, this is the player view! \n")
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
        print("The game rules are simple:\n")
        print("1 . The puzzle word is 3 to 5 letters long\n")
        print("2 . The puzzle word has no numbers or special characters\n")
        print("3 . Please guess according to the puzzle word format\n")
        print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
        print(". . . waiting for the researcher to choose a word . . . \n")

        #game in process
        puzzle_word = ''
        got_puzzle_word = False
        while got_puzzle_word != True:
            #expected: from researcher: {[puzzle_word]:some message}
            data, server = sock.recvfrom(recv_buff_size)
            data = data.decode()
            if('[puzzle_word]' in data):
                puzzle_word = find_substring( data, ']:', '}' )
                got_puzzle_word = True

        print('researcher successfully sent a puzzle word\n')

        guess = ' ' #initial value
        show_once = False

        while guess.lower() != puzzle_word.lower():
            guess = input("Please enter a guess: ")
            data_check = ( OnlyLetters(guess) and LengthCheck(guess))
            print("\n")
            while (data_check == False):
                guess = input("Please follow the game rules! Try another guess: ")
                data_check = ( OnlyLetters(guess) and LengthCheck(guess))
                print("\n")

            #let users know about the help option
            if (show_once == False) and (guess != puzzle_word):
                print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
                print("By the way, you can request help from the researcher now or later!\n")
                print("You just have to type 'help'\n")
                print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* \n")
                show_once = True;

            message_id = random_int(10,1,9)
            message_id = str(message_id)

            if guess != 'help':

                #get the correct letters only
                if(guess != 'help'): correct_letters = match_letters(puzzle_word, guess)

                #send the correct letters to Ubuntu
                message_id = random_int(10,1,9)
                message_id = str(message_id)
                send_buff = my_id+'->'+ubuntu_id+"#<msg_id:"+message_id+">{[letters]:"+str(correct_letters)+"}"
                sock.sendto(send_buff.encode(), server)

                #wait to recieve confirmation from server that the message was forwarded successfully
                data, server = sock.recvfrom(recv_buff_size)
                data = data.decode()
                if('success' not in data): print('letters not successfully forwarded to ubuntu\n')

                #print the correct letters to the player
                print("The shown letters are correct: " + correct_letters)

                #expected format: client_id_1->client_id_2#<msg_id:######>{[guess]:some_message}
                send_buff = my_id+'->'+researcher_id+"#<msg_id:"+message_id+">{[guess]:"+str(guess)+"}"
                sock.sendto(send_buff.encode(), server)

                #wait to recieve a confirmation from server that the message was forwarded successfully
                data, server = sock.recvfrom(recv_buff_size)
                data = data.decode()
                if('success' in data): print('guess successfully forwarded to the researcher\n')

            elif guess == 'help':
                #send hint request to reseacher

                #expected format: client_id_1->client_id_2#<msg_id:######>{[guess]:some_message}
                send_buff = my_id+'->'+researcher_id+"#<msg_id:"+message_id+">{[hint]:"+str(guess)+"}"
                sock.sendto(send_buff.encode(), server)

                #wait to recieve a confirmation from server that the message was forwarded successfully
                data, server = sock.recvfrom(recv_buff_size)
                data = data.decode()
                if('success' in data): print('hint request successfully forwarded to the researcher\n')

                #the max hint lenght is 250 characters = 512 - 262
                #expected: from researcher: {[hint]:some message}
                data, server = sock.recvfrom(recv_buff_size)
                data = data.decode()
                hint = find_substring( data, ']:', '}' )
                if len(hint) == 0:
                    print("\nthe researcher did not give you a hint")
                else:
                    print("hint: " + hint + "\n")
            else:
                print("default")

        print("Congratulation, you guessed the word correctly!")

    #case 3: user gives inputs other than stop and start
    else:
        print("\nEnter 'stop' to close the game and 'start' to begin the game")
