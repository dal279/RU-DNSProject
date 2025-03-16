import socket

# Load TS2 database
def load_database(filename):
    database = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 2:
                domain, ip = parts
                database[domain.lower()] = ip
    return database

# Start TS2 Server
def start_ts2_server(port):
    database = load_database("ts2database.txt")
    
    ts2_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ts2_socket.bind(("0.0.0.0", port))
    
    print(f"TS2 Server listening on port {port}")

    while True:
        message, client_address = ts2_socket.recvfrom(1024)
        query = message.decode().split()
        
        if len(query) < 4 or query[0] != "0":
            continue  # Ignore malformed messages
        
        domain = query[1].lower()
        query_id = query[2]

        # Check if domain is in TS2 database
        if domain in database:
            response = f"1 {domain} {database[domain]} {query_id} aa"
        else:
            response = f"1 {domain} 0.0.0.0 {query_id} nx"

        # Send response back
        ts2_socket.sendto(response.encode(), client_address)
        
        # Log the response
        with open("ts2responses.txt", "a") as log_file:
            log_file.write(response + "\n")

# Run TS2 server
if __name__ == "__main__":
    TS2_PORT = 47000  # Define the TS2 port
    start_ts2_server(TS2_PORT)
