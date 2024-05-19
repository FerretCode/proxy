import socket
import threading
import signal
import os

run = True

port = 3000 if os.getenv('PORT') is None else int(os.getenv('PORT'))

print(f"Starting proxy server on port {port}...")

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(10)
    print(f"Proxy server listening on port {port}...")
except Exception as e:
    print(f"Failed to start server: {e}")
    exit(1)

def get_socket_data(sock: socket.socket) -> bytes:
    request = b''
    sock.settimeout(1)
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            request += data
        except socket.timeout:
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break
    return request

def handle_client_request(client: socket.socket):
    dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        request = get_socket_data(client)
        print(f"Received request: {request.decode('utf-8', errors='ignore')}")

        host, port = get_target_from_request(request)
        print(f"Connecting to target {host}:{port}")

        dest.connect((host, port))
        dest.sendall(request)

        while True:
            data = dest.recv(1024)
            if len(data) > 0:
                client.sendall(data)
            else:
                break
    except Exception as e:
        print(f"Error handling client request: {e}")
    finally:
        dest.close()
        client.close()

def get_target_from_request(request: bytes):
    request = bytes(request.decode("utf-8").lower(), "utf-8")
    host_string_start = request.find(b'host: ') + len(b'host: ')
    host_string_end = request.find(b'\r\n', host_string_start)

    host_string = request[host_string_start:host_string_end].decode("utf-8")

    port_pos = host_string.find(":")
    if port_pos == -1:
        return host_string, 80
    host = host_string[:port_pos]
    port = int(host_string[port_pos + 1:])
    return host, port

def handle_stop_signals(signum, frame):
    global run
    run = False

signal.signal(signal.SIGINT, handle_stop_signals)
signal.signal(signal.SIGTERM, handle_stop_signals)

while run:
    try:
        client, addr = server.accept()
        print(f"New connection from {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client_request, args=(client,))
        client_handler.start()
    except Exception as e:
        print(f"Error accepting connections: {e}")

server.close()
