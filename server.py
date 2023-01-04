import paho.mqtt.client as mqtt
from datetime import datetime
import json
import os
import time

# Membuat objek client MQTT
client = mqtt.Client()

# Callback ketika client server terhubung dengan broker
def on_connect(client, userdata, flags, rc):
    os.system("cls")
    print("Connecting to broker . . .")
    time.sleep(2)
    if (rc == 0):
        print("Connected to broker\n")
    else:
        print("Connection failed")
    
# Function untuk menginterpretasikan message untuk dimasukkan ke dalam beberapa variabel
def msg_interpreter(msg):
    client = msg["client"]
    name = msg["name"]
    code = msg["code"]
    dest = msg["destination"]
    # Mengembalikan value dari masing-masing variabel
    return (client, name, code, dest)

# Callback ketika client server menerima pesan
def on_message(client, userdata, msg):
    # Decode message dari bytes ke string
    message = msg.payload.decode()  
    # Mengkonversi message yang diterima (string JSON) ke dalam bentuk dictionary kembali
    data = json.loads(message)
    # Variabel untuk menampung kembalian dari function msg_interpreter()
    client, name, code, dest = msg_interpreter(data)
    current_time = datetime.now().strftime('%H:%M:%S')

    if (client == "SMTown"):
        if (code == "Add"):
            psn = "[SMTOWN] " + name + " publish a new added concert to "+ dest + " at " + current_time + "\n"
        elif (code == "Delete"):
            psn = "[SMTOWN] " + name + " publish a canceled concert to "+ dest + " at " + current_time + "\n"
    elif (client == "YG"):
        if (code == "Add"):
            psn = "[YG Ent.] " + name + " publish a new added concert to "+ dest + " at " + current_time + "\n"
        elif (code == "Delete"):
            psn = "[YG Ent.] " + name + " publish a canceled concert to "+ dest + " at " + current_time + "\n"
    elif (client == "User"):
        if (code == "Subs"):
            psn = "[User] user with username: " + name + " subscribed " + dest + " at " + current_time + "\n"
        elif (code == "Book"):
            psn = "[User] user with username: " + name + " books concert ticket(s) from " + dest + " at " + current_time + "\n"
    print(psn)

# Client membuat koneksi dengan broker
client.on_connect = on_connect
client.connect("broker.hivemq.com", 1883)

client.subscribe("user")
client.subscribe("smtown")
client.subscribe("yg")

# Memanggil callback on_message
client.on_message = on_message

client.loop_forever()