import socket
import sys

# Function to send a query and receive a response
def send_query(server_ip, server_port, domain, query_id, mode):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(5)  # Set timeout for responses

    query = f"0 {domain} {query_id} {mode}"
    client_socket.sendto(query.encode(), (server_ip, server_port))

    try:
        response, _ = client_socket.recvfrom(1024)
        return response.decode()
    except socket.timeout:
        return None  # No response received

# Function to resolve domain using iterative or recursive mode
def resolve_domain(rs_ip, rs_port, domain, mode):
    query_id = "1234"  # A sample query ID
    log
