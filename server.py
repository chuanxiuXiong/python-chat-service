import sys, getopt
import socket
import threading 
import time

def unr_client(f, dest, serverthreads, msg, name):
    while 1:
        time.sleep(1)
        if dest not in serverthreads:
            continue
        log_output(f, "recvfrom {} {}".format(name, msg))
        serverthreads[dest].sendall("recvfrom {} {}".format(name,msg))
        break
    return 

def recv_msg(f, conn, addr, name, serverthreads, handler, end):
    while True:
        time.sleep(1)
        try:
            data = conn.recv(1024)
        except:
            if end == 0:
                end = 1
                break
        if not data:
            break
        d_a = data.split()
        d_t = d_a[0]
        if d_t == "register":
            log_output(
            f, "received register {} from host {} port {}".format(name, addr[0], addr[1]))
            print("{} registered from host {} port {}".format(name, addr[0], addr[1]))
            msg = "welcome {}".format(name)
            conn.sendall(msg)
        elif d_t == "sendto":
            dest = d_a[1]
            msg = data[(len(dest) + len(d_t) + 2):]
            log_output(f, "sendto {} from {} {}".format(dest, name, msg))
            send_msg(f, msg, serverthreads, dest, name, handler)    
    conn.close()

def send_msg(f, msg, serverthreads, dest, name, handler):
    if dest in serverthreads:
        conn = serverthreads[dest]
        try:
            conn.sendall("recvfrom {} {}".format(name,msg))
            log_output(
                        f, "recvfrom {} to {} {}".format(name, dest, msg))

        except:
            del serverthreads[dest]
    else:
        if handler == 1:
            log_output(f, "{} not registered with server, spawning {}".format(dest, dest))
            t = threading.Thread(target=unr_client, args=(f, dest, serverthreads, msg, name))
            t.daemon = True
            t.start()
        else:
            log_output(f, "{} not registered with server".format(dest))

def log_output(f, str):
    f.write(str + '\n')
    f.flush()
        
def main(argv):
    try:
        myopts, args = getopt.getopt(argv, "p:l:h:")
    except getopt.GetoptError as e:
        print("Usage: %s -p portno -l logfile -h handler" % sys.argv[0])
        sys.exit(2)
    if not myopts:
        print("Usage: %s -p portno -l logfile -h handler" % sys.argv[0])
        sys.exit(2) 
    portno = -1
    logfile = ''
    handler = -1
    serverthreads = {}
    end = 0
    f = ''
    for k, v in myopts:
        if k == '-p':
            portno = int(v)
        elif k == '-l':
            logfile = v
        elif k == '-h':
            handler = int(v)
    f = open(logfile, 'w')
    ip =  "127.0.0.1"
    sock = socket.socket(socket.SOCK_DGRAM)
    try:
        sock.bind((ip, portno))
    except e:
        print(e)
    log_output(f, "server started on 127.0.0.1 at port {}...".format(portno))
    sock.listen(1)

    while True:
        time.sleep(1)
        try:
            try:
                conn, addr = sock.accept()
            except KeyboardInterrupt:
                log_output(f, "terminating server..")
                exit(3)
                for k, v in serverthreads.items():
                    if v:
                        v.close()
                print("server terminated")
                break
                
            log_output(
                f, "client connection from host {} port {}".format(addr[0], addr[1]))
            name = conn.recv(1024).decode()
            try:
                t = threading.Thread(target=recv_msg, args=(f, conn, addr, name, serverthreads, handler, end))
                t.daemon = True
                t.start()
                serverthreads[name] = conn
            except:
                print("Error: unable to start thread")
        except KeyboardInterrupt:
            log_output(f, "terminating server..")
            exit(3)
            for k,v in serverthreads.items():
                if v:
                    v.close() 
            break
    # print("Input file : %s and output file: %s" % (ifile, ofile))
if __name__ == "__main__":
    main(sys.argv[1:])
