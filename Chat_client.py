
#################################################################################
# A Chat Client application. Used in the course IELEx2001 Computer networks, NTNU
#################################################################################
from socket import *
import time
# --------------------
# Constants
# --------------------
# The states that the application can be in
states = [
    "disconnected",  # Connection to a chat server is not established
    "connected",  # Connected to a chat server, but not authorized (not logged in)
    "authorized"  # Connected and authorized (logged in)
]
TCP_PORT = 1300  # TCP port used for communication
SERVER_HOST = "datakomm.work"  # Set this to either hostname (domain) or IP address of the chat server
# --------------------
# State variables
# --------------------
current_state = "disconnected"  # The current state of the system
# When this variable will be set to false, the application will stop
must_run = True
# Use this variable to create socket connection to the chat server
# Note: the "type: socket" is a hint to PyCharm about the type of values we will assign to the variable
client_socket = None  # type: socket

def quit_application():
    global must_run
    must_run = False

def send_command(command, arguments):
    global client_socket
    message = str(command)
    if arguments == '' or arguments == None: # if either argument is true
        message += '\n'                  # command + \n
    else:
        message += ' ' + str(arguments) + '\n'  # takes message + argument + \n
    client_socket.send(message.encode())        # sends to server with just command + \n or with argument if necessary


def get_servers_response():
    newline_received = False
    message = ""
    while not newline_received: # while newline = false
        character = client_socket.recv(1).decode() # reads server response and decodes
        if character == '\n': # if character = /n
            newline_received = True # stops reading
        elif character == '\r': # if character = /r
            pass  # jumps over
        else:
            message += character # else puts together message
    return message # returns message to function


def connect_to_server():
    # global variables
    global client_socket
    global current_state

    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, TCP_PORT)) # connects to socket
        current_state = "connected" # changes current state to connected
    except:
        current_state = "disconnected" # changes current to disconnect
        print('error') # prints error
        client_socket.close() # close client socket
    send_command('async', None)  # sends command to server with command async
    response = get_servers_response() # gets sever response
    print(response) # prints response
    if response == 'modeok': # if response = modeok
        print('SYNC mode active') # prints sync mode active
    else:
        print("CONNECTION NOT IMPLEMENTED!") # prints connection not implementet

def disconnect_from_server():
    # gets global variable
    global client_socket
    global current_state
    try:
        client_socket.close() # closes client socket
        current_state = 'disconnected' # changes current state to disconnect
    except socket.error as ex: # if socket does not close
        print(ex) # print socket.error


def public_messenger():
    public_m = str(input('Message: ')) # gets user to input public message
    send_command('msg', public_m) # sends msg as command to server and public message as argument
    response = get_servers_response().split() # gets server response
    if response[0] == 'msgerror': # if response with index 0 = msgerror
        print(get_servers_response()) # prints server response

def privat_message():
    # global variables
    global client_socket
    global current_state
    current_state = "authorized" # changes current state
    private_m = str(input('Privat Message: ')) # gets user to input private message
    send_command('privmsg', private_m) # sends command privmsg and argument private message
    response = get_servers_response().split() #  gets servers response
    if response[0] == 'msgerr': # if response in index 0 = msgerr
        print(get_servers_response()) # prints server response
    else:
        print('Private message was sent') # private message was sent


def userlist():
    # getting global variable
    global users
    send_command('users', None) # sends command users to server
    response = get_servers_response().split() # read response from server
    if response[0] == 'users': # if response i listindex 0 er users
        response.pop(0)
        print("list of users:") # prints list of users
        x = 0
        while x != len(response): # while length of response is unlike x
            print(response[x]) # print response
            x += 1
    run_chat_client() # call function


def inbox():
    # getting global variables
    global client_socket
    global current_state
    while True:
        send_command('inbox', None)     # calls function send_command with command
        i_inbox = get_servers_response().split()   # getting server response
        if i_inbox[1] == '0':                # if second objekt is 0
            print('inbox is empty!')     # inbox is empty, something wrong get this even if there is something in inbox
            break                      # break
        elif i_inbox[0] == 'privmsg' or i_inbox[0] == 'msg': # elif with two variables
            print(i_inbox)                 # prints inbox



def login():
    global current_state                # getting global variable
    current_state = 'connected'         # changing current state
    username = str(input('Username: '))  # make user input user name
    send_command('login', username)      # calls function with command and argument
    login_ans = get_servers_response()   # gets server response by calling function
    print(login_ans)                    # prints response
    if login_ans == 'loginok':            # if server response login ok
        current_state = 'authorized'       # change state to authorized
        print('Welcome: '+ username)       # prints welcome message
    elif login_ans == 'loginerr username already in use': # if server response is loginerr
        print('Login error! or username already taken') # error or user name is taken
        login()                                         # makes you try making username again


"""
The list of available actions that the user can perform
Each action is a dictionary with the following fields:
description: a textual description of the action
valid_states: a list specifying in which states this action is available
function: a function to call when the user chooses this particular action. The functions must be defined before
            the definition of this variable
"""
available_actions = [
    {
        "description": "Connect to a chat server",
        "valid_states": ["disconnected"],
        "function": connect_to_server
    },
    {
        "description": "Disconnect from the server",
        "valid_states": ["connected", "authorized"],
        "function": disconnect_from_server
    },
    {
        "description": "Authorize (log in)",
        "valid_states": ["connected", "authorized"],
        "function": login
    },
    {
        "description": "Send a public message",
        "valid_states": ["connected", "authorized"],
        "function": public_messenger
    },
    {
        "description": "Send a private message",
        "valid_states": ["authorized"],
        "function": privat_message
    },
    {
        "description": "Read messages in the inbox",
        "valid_states": ["connected", "authorized"],
        "function": inbox
    },
    {
        "description": "See list of users",
        "valid_states": ["connected", "authorized"],
        "function": userlist
    },
    {
        "description": "Get a joke",
        "valid_states": ["connected", "authorized"],
        "function": None
    },
    {
        "description": "Quit the application",
        "valid_states": ["disconnected", "connected", "authorized"],
        "function": quit_application
    },
]

def run_chat_client():
    """ Run the chat client application loop. When this function exists, the application will stop """
    while must_run:
        print_menu()
        action = select_user_action()
        perform_user_action(action)
    print("Thanks for watching. Like and subscribe! 👍")

def print_menu():
    """ Print the menu showing the available options """
    print("==============================================")
    print("What do you want to do now? ")
    print("==============================================")
    print("Available options:")
    i = 1
    for a in available_actions:
        if current_state in a["valid_states"]:
            # Only hint about the action if the current state allows it
            print("  %i) %s" % (i, a["description"]))
        i += 1
    print()

def select_user_action():
    """
    Ask the user to choose and action by entering the index of the action
    :return: The action as an index in available_actions array or None if the input was invalid
    """
    number_of_actions = len(available_actions)
    hint = "Enter the number of your choice (1..%i):" % number_of_actions
    choice = input(hint)
    # Try to convert the input to an integer
    try:
        choice_int = int(choice)
    except ValueError:
        choice_int = -1
    if 1 <= choice_int <= number_of_actions:
        action = choice_int - 1
    else:
        action = None
    return action

def perform_user_action(action_index):
    """
    Perform the desired user action
    :param action_index: The index in available_actions array - the action to take
    :return: Desired state change as a string, None if no state change is needed
    """
    if action_index is not None:
        print()
        action = available_actions[action_index]
        if current_state in action["valid_states"]:
            function_to_run = available_actions[action_index]["function"]
            if function_to_run is not None:
                function_to_run()
            else:
                print("Internal error: NOT IMPLEMENTED (no function assigned for the action)!")
        else:
            print("This function is not allowed in the current system state (%s)" % current_state)
    else:
        print("Invalid input, please choose a valid action")
    print()
    return None

# Entrypoint for the application. In PyCharm you should see a green arrow on the left side.
# By clicking it you run the application.
if __name__== '__main__':
    run_chat_client()