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
    log_file = open("resolved.txt", "a")

    print(f"\nResolving {domain} using {mode.upper()} mode...")
    
    if mode == "rd":
        # Recursive: RS handles everything
        response = send_query(rs_ip, rs_port, domain, query_id, mode)
        if response:
            print(f"Response: {response}")
            log_file.write(response + "\n")
        else:
            print("Error: No response from RS.")

    elif mode == "it":
        # Iterative: Client follows redirections
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
                current_server_port = 46000 if current_server_ip == "ts1.com" else 47000  # TS1 or TS2
            elif flag == "nx":
                print(f"Domain {domain} does not exist.")
                break

    log_file.close()

# Main function
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 client.py <RS_IP> <RS_PORT> <domain>")
        sys.exit(1)

    rs_ip = sys.argv[1]
    rs_port = int(sys.argv[2])
    domain = sys.argv[3]

    mode = input("Enter query mode (rd for recursive, it for iterative): ").strip().lower()
    if mode not in ["rd", "it"]:
        print("Invalid mode. Use 'rd' or 'it'.")
        sys.exit(1)

    resolve_domain(rs_ip, rs_port, domain, mode)
