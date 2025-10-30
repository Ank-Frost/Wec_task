import socket
import threading

# clients=[]

host = '127.0.0.1'
port = 8080

# build the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port)) # bind it to port in the given ip

server.listen() #start listening

cmds=['SET','GET','DEL']
data={} # This is our in-memory store, 

def resp_encode(msg_list):
    cmd = ""
    cmd += "*" + str(len(msg_list)) # Array *[no. of elements]
    for arg in msg_list:
        cmd += "\r\n" + "$" + str(len(arg)) # Bulk String 
        cmd += "\r\n" + arg
    cmd += "\r\n" # Terminating CRLF
    return cmd

def req_decode(msg):
    sp = msg.split('\r\n')
    cnt = int(sp[0][1:]) # Correctly gets count
    cmd = []
    # Loop 'cnt' times to get all args
    for i in range(cnt):
        # The args are at index 2, 4, 6, etc.
        cmd.append(sp[(i*2) + 2])
    return cmd # Return the parsed command


def handle_set(key, value, client_socket):
    try:
        data[key] = value
        client_socket.send(resp_encode(["OK"]).encode()) # Send to specific client
    except Exception as e:
        print(e)
        client_socket.send(resp_encode([str(e)]).encode()) # Send error to specific client

def handle_get(key, client_socket):
    try:
        # .get() to safely check for key
        value = data.get(key)
        if value is None:
            client_socket.send(resp_encode(["(nil)"]).encode()) # "Not found" reply
        else:
            client_socket.send(resp_encode([str(value)]).encode()) # Send value
    except Exception as e:
        print(e)
        client_socket.send(resp_encode([str(e)]).encode())

def handle_del(key, client_socket):
    try:
        # Check if key exists before deleting
        if key in data:
            del data[key] # Actually delete the key
            client_socket.send(resp_encode(["(integer) 1"]).encode()) # Reply with 1 (success)
        else:
            client_socket.send(resp_encode(["(integer) 0"]).encode()) # Reply with 0 (not found)
    except Exception as e:
        print(e)
        client_socket.send(resp_encode([str(e)]).encode())

def client_cmd_handler(cmd, client_socket): # Must accept client_socket
    if not cmd: # Handle empty command
        return
        
    c = cmd[0].upper() # Use .upper() to accept 'set' or 'SET'
    
    try:
        if c == 'SET' and len(cmd) == 3:
            handle_set(cmd[1], cmd[2], client_socket) # Pass socket
        elif c == 'GET' and len(cmd) == 2:
            handle_get(cmd[1], client_socket) # Pass socket
        elif c== 'DEL' and len(cmd) == 2:
            handle_del(cmd[1], client_socket) # Pass socket
        else :
            e = f"ERR wrong number of arguments for '{c}' or unknown command"
            print(e)
            client_socket.send(resp_encode([e]).encode())
    except Exception as e:
        client_socket.send(resp_encode([f"ERR {e}"]).encode())




def handle_client (client_socket, addr):
    print(f"Handling connection from {addr}")
    while True :
        try:
            # Receive the request
            msg = client_socket.recv(1024).decode()
            if not msg:
                # recv() returned empty means client closed connection
                raise ConnectionResetError()

            # Decode, Handle, and Respond
            cmd_list = req_decode(msg)
            client_cmd_handler(cmd_list, client_socket)

        except Exception as e:
            # Client disconnected or sent bad data
            print(f"Connection with {addr} closed. Reason: {e}")
            client_socket.close()
            break # Exit the loop and end the thread

def accept_connections():
    print(f"Server is listening on {host}:{port}")
    #infinitly accept clients
    while True:
        client_socket, add = server.accept()
        print(f"Connection from: {add}")
        
        # Start a thread to handle this specific client's requests
        thread = threading.Thread(target = handle_client, args = (client_socket, add))
        thread.start()

accept_connections()