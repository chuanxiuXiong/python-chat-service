import sys
import getopt
import socket
import threading
import time

def log_output(f, str):
    f.write(str + '\n')
    f.flush()

def recv_msg(f, sock, name):
    welcome = 0
    while True:
        time.sleep(1)
        if welcome != 0:
            print("waiting for messages..") 
        try:
            data = sock.recv((1024))  # buffer size is 1024 bytes
        except:
            break
        if not data:
            break
        d_a = data.split()
        d_t = d_a[0]
        msg = data[(len(d_a[1]) + len(d_t) + 2):]

        if d_t == "welcome":
            welcome = 1
            continue
        elif d_t == "recvfrom":
            print("{} recvfrom {} {}".format(name, d_a[1], msg))
            log_output(f, "recvfrom {} {}".format(d_a[1], msg))
    log_output(f, "terminating client...")
    print("{} exit".format(name))
    sock.close()

def send_msg(msg, sock):
    sock.sendall(msg.encode())

def main(argv):
    try:
        myopts, args = getopt.getopt(argv, "s:p:l:n:")
    except getopt.GetoptError as e:
        print(str(e))
        print("Usage: %s -s serverIP -p portno -l logfile -n name" % sys.argv[0])
        sys.exit(2)
    if not myopts:
        print("Usage: %s -s serverIP -p portno -l logfile -n name" %
              sys.argv[0])
        sys.exit(2)

    portno = -1
    logfile = ''
    name = ''
    serverIP = ''
    for k, v in myopts:
        if k == '-p':
            portno = int(v)
        elif k == '-l':
            logfile = v
        elif k == '-s':
            serverIP = v
        elif k == '-n':
            name = v
    f = open(logfile, 'w')
    sock = socket.socket(socket.SOCK_DGRAM)
    log_output(f, "connecting to the server {} at port {}".format(
        serverIP, portno))
    sock.connect((serverIP, portno))
    sock.sendall(str(name).encode())
    log_output(f, "sending register message {}".format(name))
    sock.sendall("register {}".format(name))
    print("{} connected to server and registered".format(name))
    log_output(f, "received welcome")
    t = threading.Thread(target=recv_msg,args=(f, sock, name))
    t.daemon = True
    t.start()
    while 1:
        time.sleep(1)
        user_input = raw_input("")
        if user_input.lower() == 'exit':
            log_output(f, "terminating client...")
            sys.exit(1)
        else:
            send_msg(user_input, sock)
            log_output(f, user_input)
            continue
    # print("Input file : %s and output file: %s" % (ifile, ofile))
if __name__ == "__main__":
    main(sys.argv[1:])
