import socket
import sys

# Function to send a query and receive a response
def send_query(server_ip, server_port, domain, query_id, mode):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.settimeout(5)  # Set timeout for responses
        client_socket.connect((server_ip, server_port))

        query = f"0 {domain} {query_id} {mode}"
        client_socket.sendall(query.encode())

        try:
            response = client_socket.recv(1024).decode()
            return response
        except socket.timeout:
            return None  # No response received

# Function to resolve domain using iterative or recursive mode
def resolve_domain(rs_ip, rs_port, domain, query_id, mode, log_file):
    print(f"\nResolving {domain} using {mode.upper()} mode...")

    if mode == "rd":
        # Recursive mode: RS handles everything
        response = send_query(rs_ip, rs_port, domain, query_id, mode)
        if response:
            print(f"Response: {response}")
            log_file.write(response + "\n")
        else:
            print("Error: No response from RS.")

    elif mode == "it":
        # Iterative mode: Client follows redirections
        current_server_ip = rs_ip
        current_server_port = rs_port

        while True:
            response = send_query(current_server_ip, current_server_port, domain, query_id, mode)
            
            if not response:
                print("Error: No response received.")
                break

            print(f"Response: {response}")
            log_file.write(response + "\n")
            parts = response.split()

            if len(parts) < 5:
                print("Error: Malformed response.")
                break

            flag = parts[4]
            if flag == "aa":
                print(f"Resolved: {domain} -> {parts[2]}")
                break  # Found the IP address
            elif flag == "ns":
                current_server_ip = parts[2]  # Follow redirection
            elif flag == "nx":
                print(f"Domain {domain} does not exist.")
                break

# Main function
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 client.py <RS_IP> <RS_PORT>")
        sys.exit(1)

    rs_ip = sys.argv[1]
    rs_port = int(sys.argv[2])

    # Read hostnames.txt
    try:
        with open("hostnames.txt", "r") as f:
            domains = [line.strip().split() for line in f.readlines()]
    except FileNotFoundError:
        print("Error: hostnames.txt not found.")
        sys.exit(1)

    log_file = open("resolved.txt", "w")  # Overwrite previous results
    query_id = 1  # Start query ID from 1

    for domain_info in domains:
        if len(domain_info) != 2:
            print(f"Skipping malformed entry: {domain_info}")
            continue

        domain, mode = domain_info
        resolve_domain(rs_ip, rs_port, domain, str(query_id), mode, log_file)
        query_id += 1  # Increment query ID

    log_file.close()
    print("\nAll queries resolved. Check resolved.txt for details.")
