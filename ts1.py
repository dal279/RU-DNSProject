import socket

# Load TS1 database
def load_database(filename):
    database = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 2:
                domain, ip = parts
                database[domain.lower()] = ip
    return database

# Start TS1 Server
def start_ts1_server(port):
    database = load_database("ts1database.txt")
    
    ts1_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ts1_socket.bind(("0.0.0.0", port))
    
    print(f"TS1 Server listening on port {port}")

    while True:
        message, client_address = ts1_socket.recvfrom(1024)
        query = message.decode().split()
        
        if len(query) < 4 or query[0] != "0":
            continue  # Ignore malformed messages
        
        domain = query[1].lower()
        query_id = query[2]

        # Check if domain is in TS1 database
        if domain in database:
            response = f"1 {domain} {database[domain]} {query_id} aa"
        else:
            response = f"1 {domain} 0.0.0.0 {query_id} nx"

        # Send response back
        ts1_socket.sendto(response.encode(), client_address)
        
        # Log the response
        with open("ts1responses.txt", "a") as log_file:
            log_file.write(response + "\n")

# Run TS1 server
if __name__ == "__main__":
    TS1_PORT = 46000  # Define the TS1 port
    start_ts1_server(TS1_PORT)
