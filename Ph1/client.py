import socket
import threading

#now we make a client socket need to connect it to server
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 

host = '127.0.0.1'
port = 8080

client.connect((host,port))
# now we r connected

def req_encode(msg_list): 
    cmd = ""
    cmd += "*" + str(len(msg_list)) # Array *[no. of elements]
    for arg in msg_list:
        cmd += "\r\n" + "$" + str(len(arg)) # Bulk String 
        cmd += "\r\n" + arg
    cmd += "\r\n" # Terminating CRLF
    return cmd


def send_msgs():
    try:
        while True:
            # Get input string from user
            msg_str = input("> ") 
            
            if msg_str == 'disconnect':
                client.close()
                exit(0)
            
            # Split the string into a list: "SET mykey hello" -> ['SET', 'mykey', 'hello']
            msg_list = msg_str.split()
            
            if not msg_list: # Handle empty input
                continue
                
            # Encode the list and send
            client.send(req_encode(msg_list).encode())
            
    except Exception as e:
        print(f"Error sending message: {e}")
        client.close()
        exit(1)

def recive_msgs():
    while True:
        try:
            # Receive the server's response
            recv_msg = client.recv(1024).decode()
            if not recv_msg:
                # Server closed the connection
                print("\nServer connection lost.")
                client.close()
                exit(0)
            
            # Print the raw (but decoded) response
            print(f"SERVER: {recv_msg.strip()}")
        
        except Exception as e:
            print(f"\nError receiving message: {e}")
            client.close()
            exit(1)


def msg_handle(client):
    # name = input("Enter name :")
    # client.send(name.encode())
    
    print("Connected to server. Type commands (e.g., 'SET key value', 'GET key') or 'disconnect'.")

    thread = threading.Thread(target=send_msgs,args=())
    thread.start()

    recive_msgs() # Run receiver in the main thread

if __name__ == '__main__':
    msg_handle(client)