import csv
import socket
import select
import time

# Set up two UDP sockets
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1.bind(('0.0.0.0', 5006))  # Port for ESP32 (temperature/humidity)

sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2.bind(('0.0.0.0', 5005))  # Port for robot coordinates

sockets = [sock1, sock2]

# Store latest temperature and humidity
latest_temp_hum = None

# Open CSV file in append mode
csv_file = open('data_log.csv', mode='a', newline='')
csv_writer = csv.writer(csv_file)

# Write header if file is new
csv_writer.writerow(["Timestamp", "Coordinate", "Temperature,Humidity"])

print("Listening...")

while True:
    readable, _, _ = select.select(sockets, [], [])
    for s in readable:
        data, addr = s.recvfrom(1024)
        if s == sock1:
            try:
                latest_temp_hum = data.decode('utf-8')  # e.g., "23.45,56.78"
            except UnicodeDecodeError as e:
                print("Temp/Hum decode error:", e)
        elif s == sock2:
            try:
                coordinate = data.decode('utf-8')
            except UnicodeDecodeError as e:
                coordinate = str(data)
                print("Coordinate decode error:", e)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f"[{timestamp}] Coordinate: {coordinate} | Temp/Hum: {latest_temp_hum}")
            # Write data to CSV
            csv_writer.writerow([timestamp, coordinate, latest_temp_hum])
            csv_file.flush()  # Flush to disk