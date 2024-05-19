import socket
import threading
import signal
import os

run = True

print(os.getenv('PORT'))

port = 3000 if os.getenv('PORT') == None else int(os.getenv('PORT'))

print(port)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', port))
server.listen(10)

print(f"Proxy server listening on port {port}...")

def get_socket_data(socket: socket.socket) -> bytes:
  request = b''

  while True:
    try:
      data = socket.recv(1024)

      request = request + data
    except:
      break

  return request

def handle_client_request(client: socket.socket):
  request = b''

  client.setblocking(False)

  request = get_socket_data(client)

  print(request.decode('utf-8'))

  host, port = get_target_from_request(request)

  print(host, port)

  dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  dest.connect((host, port))
  dest.sendall(request)

  while True:
    try:
      data = dest.recv(1024) 

      if len(data) > 0:
        print(data.decode('utf-8'))
        client.sendall(data)
    except:
      break

  dest.close()
  client.close()

def get_target_from_request(request: bytes):
  host_string_start = request.find(b'Host: ') + len(b'Host: ')
  host_string_end = request.find(b'\r\n', host_string_start)

  host_string = request[host_string_start:host_string_end].decode("utf-8")

  target = host_string.find("/")

  if target < 1:
    target = len(host_string)

  host = ''
  port = host_string.find(":")  

  if port < 1 or target < port:
    port = 80
    host = host_string[:target]
  else:
    port = int((host_string[port + 1:])[:target - port - 1 ])
    host = host_string[port]

  return host, port

def handle_stop_signals(signum, frame):
  global run
  run = False

signal.signal(signal.SIGINT, handler=handle_stop_signals)
signal.signal(signal.SIGTERM, handler=handle_stop_signals)

while run:
  client, addr = server.accept()

  print(f"New connection from {addr[0]}:{addr[1]}")

  client_handler = threading.Thread(target=handle_client_request, args=(client,))

  client_handler.start()
