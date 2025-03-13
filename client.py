import socket
import sys

# Function to send a query and receive a response
def send_query(server_ip, server_port, domain, query_id, mode):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:  # Use UDP
        client_socket.settimeout(5)  # Set timeout for responses
        query = f"0 {domain} {query_id} {mode}"
        client_socket.sendto(query.encode(), (server_ip, server_port))

        try:
            response, _ = client_socket.recvfrom(1024)  # Receive UDP response
            return response.decode()
        except socket.timeout:
            return None 

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
        visited_servers = set()  # Track visited servers to prevent loops

        while True:
            if (current_server_ip, current_server_port) in visited_servers:
                print("Error: Detected redirection loop. Stopping resolution.")
                break

            visited_servers.add((current_server_ip, current_server_port))

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
                next_server_ip = parts[2]
                next_server_port = int(parts[3])

                # Prevent looping back to the same server
                if next_server_ip == current_server_ip and next_server_port == current_server_port:
                    print("Error: Circular redirection detected.")
                    break
                
                current_server_ip = next_server_ip
                current_server_port = next_server_port
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
