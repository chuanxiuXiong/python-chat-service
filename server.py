import sys
import getopt
import socket
import threading
import time
import client


def recv_msg(f, conn, addr, name, serverthreads, socketToServers, handler, end, overlay, socket_TCP_r, ip, portno):
    while True:
        time.sleep(1)
        try:
            data = conn.recv(1024)
        except:
            print("can't receive from the conn")
            exit(2)
        if not data:
            break
        d_a = data.split()
        d_t = d_a[0]
        if d_t == "register":
            log_output(
                f, "received register {} from host {} port {}".format(name, addr[0], addr[1]))
            print("{} registered from host {} port {}".format(
                name, addr[0], addr[1]))
            msg = "welcome {}".format(name)
            conn.sendall(msg)
        else:
            dest = d_a[1]
            if 1 == 1:
                if overlay:
                    dest = d_a[1]
                    name = d_a[3]
                    msg = data[(len(dest) + len(d_t) +
                                len("from ") + len(name) + 3):]
                    log_output(
                        f, "sendto {} from {} {}".format(dest, name, msg))
                    send_msg(f, msg, serverthreads, socketToServers, dest,
                             name, handler, overlay)
                elif d_t == "sendto":
                    msg = data[(
                        len(dest) + len(d_t) + 2):]
                    if socket_TCP_r != '':
                        if check_if_exists(socket_TCP_r, dest) == "False":
                            log_output(
                                f, "sendto {} from {} {}".format(dest, name, msg))
                            log_output(
                                f, "{} not registered with server".format(dest))
                            log_output(
                                f, "sending message to server overlay {}".format(msg))
                            t = threading.Thread(target=spwaned_client, args=(
                                f, msg, serverthreads, socketToServers, dest, name, handler, ip, portno))
                            t.daemon = True
                            t.start()
                    else:
                        log_output(
                            f, "sendto {} from {} {}".format(dest, name, msg))
                        send_msg(f, msg, serverthreads, socketToServers, dest,
                                 name, handler, overlay)
    conn.close()


def spwaned_client(f, msg, serverthreads, socketToServers, dest, name, handler, ip, portno):
    # spwaning client process
    log_output(f, "received spwan client from registrar")
    sock_UDP_spwaned = socket.socket(socket.SOCK_DGRAM)
    sock_UDP_spwaned.connect((ip, portno))
    sock_UDP_spwaned.sendall(str(dest).encode())
    log = open('spwaned_{}.txt'.format(dest), 'w')
    log_output(log, "connecting to the server {} at port {}".format(
        ip, portno))
    log_output(log, "sending register message {}".format(dest))
    sock_UDP_spwaned.sendall("register {}".format(dest))
    print("{} connected to server and registered".format(dest))
    log_output(log, "received welcome")
    t = threading.Thread(
        target=client.recv_msg, args=(log, sock_UDP_spwaned, name))
    t.daemon = True
    t.start()
    # pause for a while since we want the the client to be registered
    time.sleep(3)
    # sending the buffered message to the client
    send_msg(f, msg, serverthreads,
             socketToServers, dest, name, handler, False)


def send_msg(f, msg, serverthreads, socketToServers, dest, name, handler, overlay):
    if dest in serverthreads:
        conn = serverthreads[dest]
        try:
            conn.sendall("recvfrom {} {}".format(name, msg))
            log_output(
                f, "recvfrom {} to {} {}".format(name, dest, msg))
        except:
            print("exception when sending to client")
            del serverthreads[dest]
    else:
        log_output(
            f, "{} not registered with server".format(dest))
        if not overlay:
            log_output(f, "sending message to server overlay {}".format(msg))
            for s_conn in socketToServers:
                s_conn.sendall("sendto {} from {} {}".format(dest, name, msg))

        # if handler == 1:
            # t = threading.Thread(target=unr_client, args=(
            #     f, dest, serverthreads, msg, name))
            # t.daemon = True
            # t.start()


def recv_server(f, socketserver_TCP, serverThreads, socketToServers, handler, end, socket_TCP_r, ip, portno):
    while True:
        time.sleep(1)
        try:
            s_conn, s_addr = socketserver_TCP.accept()
        except:
            print("Unable to add connection")
        socketToServers.add(s_conn)
        log_output(f, "server joined overlay from host {} port {}".format(
            s_addr[0], s_addr[1]))
        try:
            # listen to servers" overlay "requests"
            t = threading.Thread(target=recv_msg, args=(
                f, s_conn, s_addr, "server", serverThreads, socketToServers,
                handler, end, True, socket_TCP_r, ip, portno))
            t.daemon = True
            t.start()
        except:
            print("Error: unable to start thread")


def recv_client(f, serversocket_UDP, serverthreads, socketToServers, handler, end, socket_TCP_r, ip, portno):
    while True:
        time.sleep(1)
        conn, addr = serversocket_UDP.accept()
        log_output(
            f, "client connection from host {} port {}".format(addr[0], addr[1]))
        name = conn.recv(1024).decode()
        if socket_TCP_r != '':
            socket_TCP_r.sendall('register {}'.format(name))
        try:
            t = threading.Thread(target=recv_msg, args=(
                f, conn, addr, name, serverthreads, socketToServers, handler, end, False, socket_TCP_r, ip, portno))
            t.daemon = True
            t.start()
            serverthreads[name] = conn
        except:
            print("Error: unable to start thread")


def check_if_exists(sock_TCP_r, dest):
    sock_TCP_r.sendall(dest)
    try:
        return (sock_TCP_r.recv(1024))
    except:
        print("can't hear back from the registrar")


def log_output(f, str):
    f.write(str + '\n')
    f.flush()


def main(argv):
    # variale declarations
    portno = -1
    logfile = ''
    handler = -1
    serverthreads = {}
    socketToServers = set()
    end = 0
    serverOverlayIP = ''
    serverOverlayPort = -1
    overlayPort = -1
    f = ''
    registrarIP = ''
    registrarPort = -1
    err = False
    requiredFields = [False] * 4

    # getting arguments from the command line
    for i in range(0, len(argv), 2):
        flag = argv[i]
        value = argv[i+1]
        if flag == '-s':
            serverOverlayIP = value
        elif flag == '-t':
            serverOverlayPort = int(value)
        elif flag == '-o':
            overlayPort = int(value)
            requiredFields[0] = True
        elif flag == '-p':
            portno = int(value)
            requiredFields[1] = True
        elif flag == '-l':
            logfile = value
            requiredFields[2] = True
        elif flag == '-h':
            handler = int(value)
            requiredFields[3] = True
        elif flag == '-rip':
            registrarIP = value
        elif flag == '-rport':
            registrarPort = int(value)
        else:
            err = True
    # check if all required fields are filled in
    for requiredField in requiredFields:
        if requiredField == False:
            err = True
            break
    if err:
        print("Usage error")
        exit(0)

    f = open(logfile, 'w')
    ip = socket.gethostbyname(socket.gethostname())
    serversocket_UDP = socket.socket(socket.SOCK_DGRAM)
    serversocket_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_TCP_r = ''
    if handler == 1:
        socket_TCP_r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_TCP_r.connect((registrarIP, registrarPort))
    try:
        serversocket_UDP.bind((ip, portno))
        serversocket_TCP.bind((ip, overlayPort))
    except:
        print("Unable to bind to ip and port")
    log_output(f, "server started on {} at port {}...".format(ip, portno))
    log_output(
        f, "server overlay started at port {}".format(overlayPort))

    # connect with the other server and receive "overlay" request
    if serverOverlayIP != '':
        sock_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_TCP.connect((serverOverlayIP, serverOverlayPort))
        socketToServers.add(sock_TCP)
        t = threading.Thread(target=recv_msg, args=(
            f, sock_TCP, (serverOverlayIP,
                          serverOverlayPort), "server", serverthreads, socketToServers,
            handler, end, True, socket_TCP_r, ip, portno))
        t.daemon = True
        t.start()

    # accepting connections from other server
    serversocket_TCP.listen(1)
    t = threading.Thread(target=recv_server, args=(
        f, serversocket_TCP, serverthreads, socketToServers, handler, end, socket_TCP_r, ip, portno))
    t.daemon = True
    t.start()

    # accepting connections from clients
    serversocket_UDP.listen(1)
    t = threading.Thread(target=recv_client, args=(
        f, serversocket_UDP, serverthreads, socketToServers, handler, end, socket_TCP_r, ip, portno))
    t.daemon = True
    t.start()

    try:
        while(1):
            continue
    except KeyboardInterrupt:
        log_output(f, "terminating server...")
        for k, v in serverthreads.items():
            if v:
                v.close()
        for v in socketToServers:
            if v:
                v.close()
        exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
