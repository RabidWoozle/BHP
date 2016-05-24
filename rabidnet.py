#!/usr/bin/env python

import sys
import socket
import getopt
import threading
import subprocess

# globals
listen      = False
command     = False
upload      = False
execute     = ""
target      = ""
upload_dest = ""
port        = 0

def usage ():
    print "RABID Net Tool"
    print
    print "Usage: rabidnet.py -t target_host -p port"
    print "-l --listen    - listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run - execute a given file"
    print "-c --command - initialize a command shell"
    print "-u --upload=destination  - upon receiving connection upload a file and write to destination"
    print
    print
    print "Examples:"
    print "rabidnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "rabidnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "rabidnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./rabidnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)

def client_sender(buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #connect to the host
        client.connect((target,port))

        if len(buffer):
            client.send(buffer)
        while True:

            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response+= data

                if recv_len < 4096:
                    break

            print response,

            #wait for input
            buffer = raw_input("")
            buffer += "\n"
            #send it off
            client.send(buffer)

    except:
        print "[*] Exception! went to shit, exiting."
        client.close()

            


def server_loop():
    global target

    if not len(target):
        target = "0.0.0.0"
        
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((target,port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    #trim newline
    command = command.rstrip()

    #run the command and get output back
    try:
        output = subprocess.check_output(command,stderr=subprocess.SDTOUT, shell=True)
    except:
        output = "failed to execute command. \r\n"
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_dest):
        #read all the bytes and write to destination
        
        file_buffer = ""

        #read loop
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        try:
            file_descriptor = open(upload_dest,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send("Successfully saved file to %s\r\n" % upload_dest)

            if len(execute):

                #run the command
                output = run_command(execute)
                client_socket.send(output)

            if command:
                while True:
                    #show prompt
                    client_socket.send("<RBD:#> ")
                    cmd_buffer = ""
                    while "\n" not in cmd_buffer:
                        cmd_buffer += client_socket.recv(1024)
                    response = run_command(cmd_buffer)

                    client_socket.send(response)
                    


def main():
    global listen
    global port
    global execute
    global comman
    global upload_dest
    global target

    if not len(sys,argv[1:]):
        usage()

    try :
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu", ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_dest = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    if not listen and len(target) and port > 0:
        #read in the bugger from the commanline
        #this will block so send CTRL-D if not sending input
        #to stdin

        buffer = sys.stdin.read()

        #send data off
        client_sender(buffer)


    #listen and potentially
    #upload,exe,shell
    #depending on command options
    if listen:
        server_loop()

main()
        
        
            
        


