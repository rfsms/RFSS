import socket

def listen_for_udp_broadcast(target_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a UDP socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(("", port))  # "" means that the socket should listen on all available interfaces
    
    while True:
        data, addr = s.recvfrom(1024)  # Receive data from the socket (1024 bytes max)
        if addr[0] == target_ip:  # Check if the data comes from the target IP
            print(f"Received message from {addr}: {data.decode('utf-8')}")

    s.close()

if __name__ == "__main__":
    target_ip = "192.168.4.1"  # Change this to the IP you are expecting a message from
    port = 9932  # Change this to the port you're listening on
    listen_for_udp_broadcast(target_ip, port)
