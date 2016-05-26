import sys
import socket
import threading

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):

    server = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except:
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions")
        sys.exit(0)

    print ("[*] Listening on %s:%d" % (local_host, local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        #print out the local connection info
        print ("[==>] received incoming connection from %s:%d" % (addr[0], addr[1]))

        #start proxy
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))

        proxy_thread.start()


def hexdump(src,  length=16):
    result = []
    digits = 4
    for i in range(0,  len(src),  length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X %-*s %s" % (i, length*(digits + 1), hexa, text) )
        print(b'\n'.join(result))

def receive_from(connection):
    buffer = ""

    #2 second timeout
    connection.settimeout(2)

    try:
        #read buffer until there is no more data
        while True:
            data = connection.recv(4096)

            if not data:
                break
            buffer += data

    except:
        pass

    return buffer

def request_handler(buffer):
    #perform packet modifications
    return buffer

def response_handler(buffer):
    #perform packet modifications
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):

    #connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:

        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        #send to the response handler
        remote_buffer = response_handler(remote_buffer)

        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)

    while True:

        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("[==>] received %d bytes from localhost" % len(local_buffer))
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote")

            #receive response
            remote_buffer = receive_from(remote_socket)

            if len(remote_buffer):
                print("[<==] Received %d bytes from remote." % len(remote_buffer))
                hexdump(remote_buffer)
                remote_buffer = response_handler(remote_buffer)

                client_socket.send(remote_buffer)
                print("[<==] Sent to localhost")

            if not len(local_buffer) or not len(remote_buffer):
                client_socket.close()
                remote_socket.close()
                print("[*] No more data. Closing remote and local connections")

                break




def main():

    if len(sys.argv[1:]) != 5:
        print("Usage: ./ProxyTCP.py [localhost] [localport] [remotehost] [remoteport] [receivefirst]")
        print("Example: ./ProxyTCP.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    #get local command args
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])


    #get remote command args
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    #tells the proxy to connect and receive data
    #before sending to remote host
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

main()
