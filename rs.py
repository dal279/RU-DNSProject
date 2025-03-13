import socket

# Load database into a dictionary
def load_database(filename):
    database = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 2:
                domain, ip = parts
                database[domain.lower()] = ip
    return database

# Initialize RS Server
def start_rs_server(port):
    database = load_database("rsdatabase.txt")
    
    # UDP Socket setup
    rs_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rs_socket.bind(("localhost", port))
    
    print(f"RS Server listening on port {port}")

    while True:
        message, client_address = rs_socket.recvfrom(1024)
        query = message.decode().split()
        
        if len(query) < 4 or query[0] != "0":
            continue  # Ignore malformed messages
        
        domain = query[1].lower()
        query_id = query[2]
        query_type = query[3]

        # Check if domain is in the database
        if domain in database:
            response = f"1 {domain} {database[domain]} {query_id} aa"
        else:
            # Determine which TLD server to forward to
            if domain.endswith(".com"):
                response = f"1 {domain} {TS1_IP} {TS1_PORT} ns"
            elif domain.endswith(".edu"):
                response = f"1 {domain} {TS2_IP} {TS2_PORT} ns"
            else:
                response = f"1 {domain} 0.0.0.0 {query_id} nx"
        
        # Send response to the client
        rs_socket.sendto(response.encode(), client_address)
        
        # Log the response
        with open("rsresponses.txt", "a") as log_file:
            log_file.write(response + "\n")

# Run the RS server
if __name__ == "__main__":
    RS_PORT = 45000
    start_rs_server(RS_PORT)
