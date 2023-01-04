import paho.mqtt.client as mqtt
from prettytable import PrettyTable
import datetime
import json
import os
import time
import re

# Membuat objek client MQTT
client = mqtt.Client()

# Membuat list kosong untuk menampung jadwal konser
concerts = []

# Callback ketika client terhubung dengan broker
def on_connect(client, userdata, flags, rc):
    print("Connecting to broker . . .")
    time.sleep(2)
    if (rc == 0):
        print("Connected to broker")
    else:
        print("Connection failed")

# Function untuk menampilkan menu
def menu():
    os.system("cls")
    print("+-------------+--------------+-------------+")
    print("|           YG ENT. CONCERT ADMIN          |")
    print("+-------------+--------------+-------------+\n")

    # Membuat table
    t = PrettyTable(['No', 'Menu'])
    t.add_row(['1', 'Add concert schedule'])
    t.add_row(['2', 'Delete concert schedule'])
    t.add_row(['3', 'Show schedule'])
    t.add_row(['4', 'Exit'])
    t.align = 'l'
    print(t)

# Function untuk mengecek validitas date
def is_valid_date(date_string):
    # Mengecek kesesuaian format
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_string):
        return False

    # Mendefinisikan variabel year, month, day dengan menggunakan method split
    year, month, day = date_string.split('-')

    # Mengkonversi nilai year, month, day menjadi integer
    year = int(year)
    month = int(month)
    day = int(day)

    # Mengecek apakah year dalam range (2022 - 2100)
    if year < 2022 or year > 2100:
        return False

    # Mengecek apakah month dalam range (1 - 12)
    if month < 1 or month > 12:
        return False

    # Mengecek kesesuaian hari berdasarkan bulan
    if day < 1:
        return False
    if month in (1, 3, 5, 7, 8, 10, 12):
        if day > 31:
            return False
    elif month in (4, 6, 9, 11):
        if day > 30:
            return False
    else:
        # Mengecek pada tahun kabisat
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            if day > 29:
                return False
        else:
            if day > 28:
                return False

    # If all the checks passed, the date is valid
    return True

# Function untuk mengecek validitas time
def is_valid_time(time):
  try:
    datetime.datetime.strptime(time, '%H:%M')
    return True
  except ValueError:
    return False

# Function untuk menambahkan konser baru
def add():
    while True:
        os.system("cls")
        print("+-------------+--------------+-------------+")
        print("|              ADD NEW CONCERT             |")
        print("+-------------+--------------+-------------+\n")
        show()
        print("")

        # Mendapatkan data konser dari user/admin
        code = "Add"
        title = input("Enter the title of the concert: ")
        date = input("Enter the date of the concert (YYYY-MM-DD): ")
        time = input("Enter the time of the concert (HH:MM): ")
        performers = input("Enter the performers (comma separated): ")

        if (title == "" or is_valid_date(date) == False or is_valid_time(time) == False or performers == ""):
            print("\nThere is an invalid input, make sure input with the correct format")
            break
        else:
            # Menambahkan konser yang dibuat ke dalam list "concerts"
            concerts.append({
                "title": title,
                "date": date,
                "time": time,
                "performers": performers
            })

            # Mendefinisikan pesan berbentuk dictionary yang berisi key dan value untuk di-publish
            to_publish = ({
                "code": code, 
                "title": title,
                "date": date,
                "time": time,
                "performers": performers 
            })

            to_publish2 = ({
                "client": "YG",
                "name": "Admin",
                "code": code, 
                "destination": "subscriber"
            })

            # Mengkonversi dictionary menjadi string dalam format JSON 
            to_publish_json = json.dumps(to_publish)
            to_publish_json2 = json.dumps(to_publish2)

            # Publish pesan berisi informasi jadwal konser
            client.publish("girlband", to_publish_json)
            client.publish("yg", to_publish_json2)

            print("Concert added successfully\n")
            break

# Function untuk menghapus jadwal konser 
def delete():
    while True:
        os.system("cls")
        print("+-------------+--------------+-------------+")
        print("|              DELETE CONCERT              |")
        print("+-------------+--------------+-------------+\n")
        show()
        print("")

        # Mendapatkan data judul konser dari user
        code = "Delete"
        title = input("Enter the title of the concert you want to delete: ")

        for concert in concerts:
            if concert["title"] == title:
                date = concert["date"]
                time = concert["time"]
                performers = concert["performers"]
                concerts.remove(concert)

                # Mendefinisikan pesan berbentuk dictionary yang berisi key dan value untuk di-publish
                to_publish = ({
                    "code": code,
                    "title": title,
                    "date": date,
                    "time": time,
                    "performers": performers
                })

                to_publish2 = ({
                "client": "YG",
                "name": "Admin",
                "code": code, 
                "destination": "subscriber"
                })

                # Mengkonversi dictionary menjadi string dalam format JSON
                to_publish_json = json.dumps(to_publish)
                to_publish_json2 = json.dumps(to_publish2)

                # Publish pesan berisi informasi jadwal konser
                client.publish("girlband", to_publish_json)
                client.publish("yg" , to_publish_json2)
                msg = "\nConcert with the title " + title + " has been deleted\n"
                break

            else:
                msg = "\nYour input is invalid, make sure the title is in the concert schedule\n"
        break

    print(msg)

# Function untuk menampilkan jadwal konser
def show():
    # Membuat table 
    table = PrettyTable(["Title", "Date", "Time", "Performers"])

    # Menambahkan rows pada table
    for concert in concerts:
        table.add_row([concert["title"], concert["date"], concert["time"], concert["performers"]])

    # Print table
    print(table)
    print("")

# Client memulai loop
client.loop_start()

# Client membuat koneksi dengan broker
client.on_connect = on_connect
client.connect("broker.hivemq.com", 1883)

time.sleep(4)

while True:
    os.system("cls")

    menu()

    # Mendapatkan input pilihan menu dari user
    choice = input("Enter your choice: ")

    # Jika "1" berarti memanggil function add()
    if choice == "1":
        while True:
            add()
            choice = input("Press 'N' to add concert again, Press 'Q' to return to previous menu: ")
            if choice.upper() == 'Q':
                break

    # Jika "2" berarti memanggil function delete()            
    elif choice == "2":
        while True:
            delete()
            choice = input("Press 'D' to delete concert again, Press 'Q' to return to previous menu: ")
            if choice.upper() == 'Q':
                break
    
    # Jika "3" berarti memanggil function show() 
    elif choice == "3":
        while True:
            os.system("cls")
            print("+-------------+--------------+-------------+")
            print("|           YG CONCERT SCHEDULE            |")
            print("+-------------+--------------+-------------+\n")
            show()
            choice = input("Press 'Q' to return to previous menu: ")
            if choice.upper() == 'Q':
                break
    
    # Jika "4" berarti keluar dari program
    elif choice == "4":
        os.system("cls")
        break
    
    else:
        print("Invalid choice. Try again.")

# Client loop berhenti
client.loop_stop()