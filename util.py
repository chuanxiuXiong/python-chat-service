def unr_client(f, dest, serverthreads, msg, name):
    while 1:
        time.sleep(1)
        if dest not in serverthreads:
            continue
        log_output(f, "recvfrom {} {}".format(name, msg))
        serverthreads[dest].sendall("recvfrom {} {}".format(name, msg))
        break
    return


def recv_msg(f, conn, addr, name, serverthreads, socketToServers, handler, end, overlay):
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
            print("{} registered from host {} port {}".format(
                name, addr[0], addr[1]))
            msg = "welcome {}".format(name)
            conn.sendall(msg)
        elif d_t == "sendto":
            dest = d_a[1]
            msg = data[(len(dest) + len(d_t) + 2):]
            log_output(f, "sendto {} from {} {}".format(dest, name, msg))
            send_msg(f, msg, serverthreads, socketToServers, dest,
                     name, handler, overlay)
    conn.close()


def send_msg(f, msg, serverthreads, socketToServers, dest, name, handler, overlay):
    if dest in serverthreads:
        conn = serverthreads[dest]
        try:
            conn.sendall("recvfrom {} {}".format(name, msg))
            log_output(
                f, "recvfrom {} to {} {}".format(name, dest, msg))
        except:
            del serverthreads[dest]
    else:
        log_output(
            f, "{} not registered with server.")
        if not overlay:
            log_output(f, "sending message to server overlay {}".format(msg))
            for s_conn in socketToServers:
                s_conn.sendall("recfrom {} {}".format(name, msg))

        # if handler == 1:
            # t = threading.Thread(target=unr_client, args=(
            #     f, dest, serverthreads, msg, name))
            # t.daemon = True
            # t.start()
        else:
            log_output(f, "{} not registered with server".format(dest))


def recv_server(f, sock_TCP, socketToServers, handler, end):
    while True:
        time.sleep(1)
        try:
            s_conn, s_addr = sock_TCP.accept()
            socketToServers.add(s_connect)
            log_output(f, "server joined overlay from host {} port {}".format(
                s_addr[0], s_addr[1]))
            try:
                t = threading.Thread(target=recv_msg, args=(
                    f, s_conn, s_addr, name, serverthreads, socketToServers,
                    handler, end, True))
                t.daemon = True
                t.start()
                serverthreads[name] = conn
            except:
                print("Error: unable to start thread")

        except expression:
            print(expression)


def log_output(f, str):
    f.write(str + '\n')
    f.flush()
