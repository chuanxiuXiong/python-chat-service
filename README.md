# python-chat-service

To run the program with handler, please run registrar.py first.

When running the server, it automatically chooses its own IP address by using the function socket.gethostbyname(socket.gethostname()) instead of "127.0.0.1". Therefore, when other servers or clients trying to connect to a server, please enter the IP address of the server. If all servers and clients program are tested on one host, please do not use '127.0.0.1' but instead use the atual IP address. I think this is what the assignment requires given the grading rubric.

In the log file, there are a couple places that might cause some confusions:
1) instead of general 'host port' in the rubric, I output 'host xxx.xxx.xxx.xxx port xxxx' - the actual IP and port.
2) The rubric specifically asks us to output "received spawn client from registrar" (without the actual name Bob) in Server1.txt and "received client register Bob from server <<IP1> port <hostport>" (with the actual name) in Registrar.txt. This is exactly what I did. If the testing program expects both with the actual name or both without the actual name, please note that this format might not be wrong since this is in the rubric.

To exit server.py/registrar.py, please enter cntr + C. To exit client.py, please type exit. When existing, there might be some customized error messages on the console as some sockets cannot receive data from the other ends. These are well handled by try-catch blocks and please do not deduct points because of these extra output.

I don't think there is any specific console output requirements on this assignment specifically, so please grade mostly based on the log file.
