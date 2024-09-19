After completing the building portion do the following

run the command server as follows 'python3 command_server.py'
run the bot server as follows 'python3 bot.py'

for referance possible server commands are as follows:

    add_bot :establishes a connection with a single bot, upon complateion you will be in communication with  a single bot

    list_bots :provides a list of all bots that are controled by the server

    attack <ip address> :this command has all bots attack the given ip address

    attack_single <ip address> :attack single informs a single bot to attack the given target
    
    stop :sends a message to all bots to halt an attack
    
    exit :tells the bots to exit the bot program and will close out the command server.
     
When in communication with a single bot following the add bot command you are able to issue the following:

   help : tells you what commands are available to the bot
   
   attack <ip address> :see above

   stop :see above

   exit :see above

   wait : have the bot wait for more communications and allow he control server do other tasks such as add new bots or command all bots at the same time.
  