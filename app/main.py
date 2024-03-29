# Uncomment this to pass the first stage
import argparse
import os
import threading
import socket


def handle_client(client_socket,client_address,directory="files"):
    print(f"Connection from {client_address}")

    request_data = client_socket.recv(1024) # read data from the connection
    print(f"Received data: {request_data}")

    # Extract the path from the HTTP request
    path = request_data.decode().split(" ")[1]
    print(f"Path: {path}")    
    

    # Check if the path is "/" and respond accordingly
    if path == "/":
        response = "HTTP/1.1 200 OK\r\n\r\n" # HTTP response
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n" # HTTP response

    # Check if the path starts with "/echo/" and respond accordingly
    if path.startswith("/echo/"):
        echo_string = path[6:] # get the string after "/echo/"
        response_body = echo_string
        response_headers = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {}\r\n\r\n".format(len(response_body))
        response = response_headers + response_body # HTTP response

        # Check if the path is "/user-agent" and respond accordingly
    elif path == "/user-agent":
        headers = request_data.decode().split("\r\n")[1:] # get the headers
        user_agent = [header.split(": ")[1] for header in headers if header.startswith("User-Agent")][0] # extract User-Agent
        response_body = user_agent
        response_headers = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {}\r\n\r\n".format(len(response_body))
        response = response_headers + response_body # HTTP response

    response = response.encode()

    if request_data.decode().split(" ")[0] == "GET" and path.startswith("/files/"):
        filename = path[7:] # get the filename
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            print(f"File found Path: {filepath}")
            with open(filepath, "rb") as f:
                file_content = f.read()
                print(f"File content: {file_content}")
            response_headers = "HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {}\r\n\r\n".format(len(file_content))
            response = response_headers.encode() + file_content # HTTP response
            print(f"File response: {response}")
        else:
            print(f"File not found Path: {filepath}")
            response = "HTTP/1.1 404 Not Found\r\n\r\n" # HTTP response
            response = response.encode()
    elif request_data.decode().split(" ")[0] == "POST" and path.startswith("/files/"):
        filename = path[7:] # get the filename
        filepath = os.path.join(directory, filename)
        file_content = request_data.decode().split("\r\n\r\n")[1] # get the file content
        with open(filepath, "wb") as f:
            f.write(file_content.encode())
        response = "HTTP/1.1 201 Created\r\n\r\n" # HTTP response
        response = response.encode()

    client_socket.sendall(response) # send response
    client_socket.close()

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", help="directory to serve files from", default="files")
    args = parser.parse_args()
    directory = args.directory

    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client_socket, client_address = server_socket.accept() # wait for client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,client_address,directory))
        client_thread.start()

if __name__ == "__main__":
    main()
