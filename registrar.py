import sys
import getopt
import socket
import threading
import time


def log_output(f, str):
    f.write(str + '\n')
    f.flush()


def recv_msg(f, conn, s_addr, clientSet):
    while True:
        time.sleep(1)
        try:
            data = conn.recv(1024)
        except:
            print("can't receive from the conn")
            exit(2)
        data_a = data.split()
        data_t = data_a[0]
        if data_t == 'register':
            log_output(f, "received client register {} from server {} port {}".format(
                data_a[1], s_addr[0], s_addr[1]))
            clientSet.add(data_a[1])
        else:
            if data_t in clientSet:
                conn.sendall("True")
            else:
                conn.sendall("False")
                log_output(f, "sending spwan {} to server {} port {}".format(
                    data_t, s_addr[0], s_addr[1]))


def recv_server_req(f, serversocket_TCP_r, clientSet):
    while True:
        time.sleep(1)
        try:
            s_conn, s_addr = serversocket_TCP_r.accept()
        except:
            print("Unable to add connection")
            exit(2)
        try:
            # listen to client's name from the server
            t = threading.Thread(target=recv_msg, args=(
                f, s_conn, s_addr, clientSet))
            t.daemon = True
            t.start()
        except:
            print("Error: unable to start thread")


def main(argv):
    portno = -1
    logfile = ''
    clientSet = set()
    ip = socket.gethostbyname(socket.gethostname())
    for i in range(0, len(argv), 2):
        flag = argv[i]
        value = argv[i+1]
        if flag == '-port':
            portno = int(value)
        elif flag == '-log':
            logfile = value
    f = open(logfile, 'w')
    serversocket_TCP_r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket_TCP_r.bind((ip, portno))
    serversocket_TCP_r.listen(1)
    t = threading.Thread(target=recv_server_req, args=(
        f, serversocket_TCP_r, clientSet))
    t.daemon = True
    t.start()
    try:
        while(1):
            continue
    except KeyboardInterrupt:
        log_output(f, "terminating registrar...")
        exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
