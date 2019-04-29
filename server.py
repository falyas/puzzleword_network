#Author: Farah Alyasari, 2019 All Rights Reserved.

import socket
import string
import random
from dataclasses import dataclass

#this is a socket object for IPV4 and UDP communication
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = '127.0.0.1'
client_addr = '127.0.0.1'
server_port = 5558
recv_buff_size = 1024
send_buff = ''

#using loop back address on the local machine with an unreserved port number
#Running two processes using TCP/IP socket for communication on one computer
#is basically equivalent to running two processes on two computers individually.
#So it does not matter and the program should work either way.
address = (server_addr, server_port)
print('starting up on {} port {}'.format(*address))
sock.bind(address)

#This is a class to handle the session information
@dataclass
class session:
    state: str
    client_id: str
    client_addr: str
    client_port: int
    def switch_to_online(self):
        self.state = 'online'
    def switch_to_offline(self):
        self.state = 'ofline'

#an array of session objects
session_list = []

#Utility function: use to extract information from the data recieved
#it will always extract the first and the last which show up earlier in the string
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

#This file is used to authenticate user_profiles
#filename = 'profiles.txt'

#Utility function: Assumes there is one [id, pw] per line in the file
def authenticate_user(client_id, client_pw):
    try:
        log_file = open('profiles.txt', 'r')
        for line in log_file:
                #this is not very secure, because part of the password can still authenticate the user
                if (client_id in line) and (client_pw in line):
                    return True
                    return found
                    log_file.close()
        return False
        log_file.close()
    except FileNotFoundError:
        print('Log Info File is Not Found, Sorry!')

#Uutility fuction: Used to send back a unique connection key each time a user logs in
def get_unique_connection_key(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

while True:

    data, from_addr = sock.recvfrom(recv_buff_size)
    data = data.decode()
    from_id = find_substring(data, '','->')
    from_port = find_substring( data, '{', '}' )
    new_session = session('online', from_id, from_addr,from_port)
    session_list.append(new_session)
    print('the ' + from_id + ' is online')

    #case 1: a client wants to forward a message to another client
    #expected data: client_id_1->client_id_2#<msg_id:######>{some_message}
    if ('msg_id' in data):
        #extract the to_id and to_port to forward the message to the desired client
        to_id = find_substring(data, '->', '#')
        from_msg_id =find_substring(data, ':', '>')
        to_port = 0         #initial value
        to_state = ''       #initial value
        to_addr = ''
        for x in session_list:
            if (x.client_id == to_id):
                to_port =  x.client_port
                to_state = x.state
                to_addr = x.client_addr
                print('the ' + to_id + ' is ' + to_state)
                break;
        if to_state != 'online':
            #tell the from client that the to client is offline
            #expected send_buff: server->client_id<msg_id>Error: destination offline!
            send_buff = ('server->' + from_id + '#<' +
                        from_msg_id + '>destination is offline!')
            sock.sendto(send_buff.encode(), from_addr)
            print('the to client ' + to_id + ' is offline')
        else:
            #extract the message to be forwarded and send it to the to client
            #expected format: client_id_1->client_id_2#<msg_id:######>{some_message}
            print(data)
            forward_message = find_substring(data,'{','}')
            send_buff = 'from ' + from_id + ':{'+ str(forward_message)+'}'
            sock.sendto(send_buff.encode(), to_addr)
            #echo the message to the sending client. Note this does not necessarly mean the
            #message was successfully delivered to the client, it just means that it was
            #successfully delivered to the server and that the server forwarded it
            from_msg_id = find_substring(data,'<','>')
            send_buff = ('server->'+ to_id + '#<'+ from_msg_id+'>success')
            print(send_buff)
            sock.sendto(send_buff.encode(), from_addr)

    elif 'offline' in data:
        #turn this client to offline
        for x in session_list:
            if (x.client_id == from_id ) and (x.client_port == from_port):
                x.switch_to_offline()
                print('the ' + from_id + ' is ' + x.state)
                break;
