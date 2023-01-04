import paho.mqtt.client as mqtt
from prettytable import PrettyTable
from datetime import datetime
import sqlite3
import json
import os
import time

# List untuk menampung setiap pesan
sm_messages = []
sm_unread_messages = []
yg_messages = []
yg_unread_messages = []

# List untuk menampung jadwal konser
sm_concerts = []
yg_concerts = []


#--------------------------------------------------------------------------------------------------------------#
os.system("cls")

# Membuat koneksi dengan database (jika belum ada berarti membuat database)
conn = sqlite3.connect("userdata.db") # database untuk menyimpan informasi user

# Membuat objek cursor untuk "userdata.db"
cursor = conn.cursor()

# Mengecek apakah sudah terdapat table bernama 'users' pada 'userdata.db'
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")

# Mendapatkan hasil dari query dengan kondisi yang dicari
r = cursor.fetchone()

# Jika tidak ada, dia akan membuat table bernama 'users'
if r is None:
    cursor.execute("CREATE TABLE users (username TEXT, password TEXT)")

print("+-------------+--------------+-------------+")
print("|              LOG IN/SIGN UP              |")
print("+-------------+--------------+-------------+\n")
print("If you entered new username/password, then it will automatically created a new account\n")

# Mendapatkan user data dari input user
username = input("Enter your name: ")
password = input("Enter your password: ")

# Mengecek apakah username dan password yang diinputkan telah ada dalam database atau belum
cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))

# Mendapatkan hasil dari query dengan kondisi yang dicari
result = cursor.fetchone()

# Kondisi jika belum ada
if result is None:
    # Menambahkan username dan password yang diinputkan ke dalam database
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    # Menyimpan data
    conn.commit()
    print("Log in using a new account . . .")
    # Membuat koneksi dengan database bernama 'usernamepassword.db' (jika belum ada berarti membuat database)
    conn2 = sqlite3.connect(username + password + ".db") # database untuk menyimpan tiket yang telah di-booking user
    time.sleep(3)
else:
    print("Log in using an exsiting account ...")
    # Membuat koneksi dengan database bernama 'usernamepassword.db' (jika belum ada berarti membuat database)
    conn2 = sqlite3.connect(username + password + ".db") # database untuk menyimpan tiket yang telah di-booking user
    time.sleep(3)


#--------------------------------------------------------------------------------------------------------------#

to_print = False
# Function yang menampung program SMTown
def SMTown():

    # Callback ketika client terhubung dengan broker
    def on_connect(client, userdata, flags, rc):
        time.sleep(0)
    
    # Function untuk menginterpretasikan message untuk dimasukkan ke dalam beberapa variabel
    def msg_interpreter(msg):
        # Menambahkan message yang berbentuk dictionary ke list 'sm_concerts'
        sm_concerts.append(msg)

        code = msg["code"]
        title = msg["title"]
        date = msg["date"]
        time = msg["time"]
        performers = msg["performers"]
        # Mengembalikan value dari masing-masing variabel
        return (code, title, date, time, performers)

    # Callback ketika client menerima pesan
    def on_message(client, userdata, msg):
        global to_print 

        # Decode message dari bytes ke string
        message = msg.payload.decode()  
        # Mengkonversi message yang diterima (string JSON) ke dalam bentuk dictionary kembali
        data = json.loads(message)
        # Variabel untuk menampung kembalian dari function msg_interpreter()
        code, title, date, time, performers = msg_interpreter(data)

        current_time = datetime.now().strftime('%H:%M:%S')

        # Jika code == 'Add' berarti publisher telah menambahkan jadwal
        if (code == "Add"):
            psn = "[ SMTOWN NEW ADDED SCHEDULE | " + current_time + " ]\n" + "Title :  " + title + "\nDate :  " + date + "\nTime :  " + time + "\nPerformers :  " + performers + "\n"
        # Jika code == 'Delete' berarti publisher telah menghapus/cancel jadwal
        elif (code == "Delete"):
            psn = "[ SMTOWN CANCELED SCHEDULE | " + current_time + " ]\n" + "Title :  " + title + "\nDate :  " + date + "\nTime :  " + time + "\nPerformers :  " + performers + "\n"

        # menambahkan message/pesan/psn ke dalam list 
        sm_messages.append(psn)
        sm_unread_messages.append(psn)

        if to_print:
            print(psn)
       
    # Function untuk display semua message yang telah diterima
    def display_messages():
        # Print semua message dalam list
        for message in sm_messages:
            print(message)
  
        # Mengosongkan list unread_messages (berarti semua pesan telah dilihat/dibaca)
        sm_unread_messages = []
    
    # Function untuk membuat/meng-update table jadwal lengkap konser dengan parameter list concert dan table
    def show_schedule(concert, table):
        for concert in sm_concerts:
            # Jika code == 'Add' berarti menambahkan row
            if concert["code"] == "Add":
                title = concert["title"]
                date = concert["date"]
                time = concert["time"]
                performers = concert["performers"]
                table.add_row([title, date, time, performers])
            # Jika code == 'Delete' berarti menghapus row
            elif concert["code"] == "Delete":
                for i, row in enumerate(table._rows):
                    if row[0] == concert["title"]:
                        index = i
                        break
                # Jika row ditemukan, hapus row tersebut
                if index is not None:
                        table.del_row(index)
    
    # Function untuk menampilkan detail booking tiket
    def purchase_detail(table):
        os.system("cls")
        print("+-------------+--------------+-------------+")
        print("|              BOOKING SUCCESS             |")
        print("+-------------+--------------+-------------+\n")
        print(table)
        current_date = datetime.date(datetime.now())
        current_time = datetime.now().strftime('%H:%M:%S')
        print("Date and time of booking:", current_date, current_time)

        print("\nPress 'Q' to return to the main menu\n")
        if input().upper() == "Q":
                pass
        
    # Function untuk halaman konfirmasi booking tiket dengan salah satu parameternya adalah cursor untuk mengoperasikan/mengeksekusi database 
    def advance_ticketing(cursor2, concert_title, seat_plan, quantity, price, client):
        os.system("cls")
        print("+-------------+--------------+-------------+")
        print("|               CONFIRMATION               |")
        print("+-------------+--------------+-------------+\n")

        # Membuat table detail konser yang dibeli
        t = PrettyTable(['Title', 'Date', 'Time', 'Performers'])
        for concert in sm_concerts:
            if concert["title"] == concert_title:
                title = concert["title"]
                date = concert["date"]
                time = concert["time"]
                performers = concert["performers"]
                t.add_row([title, date, time, performers])
        print(t)
        print("")

        # Membuat table detail tiket konser yang akan di-booking
        t2 = PrettyTable(['Object', 'Detail'])
        t2.add_row(['Username', username])
        t2.add_row(['Concert title', concert_title])
        t2.add_row(['Seat plan', seat_plan])
        t2.add_row(['Quantity', quantity])
        t2.add_row(['Total price', price])
        t2.align = 'l'
        print(t2)
        print("")

        # Mendefinisikan pesan berbentuk dictionary yang berisi key dan value untuk di-publish
        to_publish = ({
            "client": "User",
            "name": username,
            "code": "Book", 
            "destination": "SMTown",
        })
        # Mengkonversi dictionary menjadi string dalam format JSON 
        to_publish_json = json.dumps(to_publish)

        result = 0
        confirm = input("Confirm your booking (y/n): ")
        if confirm.upper() == "Y":
            # Menambahkan row ke table dengan value konser yang telah dibooking
            cursor2.execute("INSERT INTO smtown (title, date, time, seat, quantity) VALUES (?, ?, ?, ?, ?)", (concert_title, date, time, seat_plan, quantity))
            conn2.commit()
            # Publish pesan
            client.publish("user", to_publish_json)
            purchase_detail(t2)
            result = 1
        elif confirm.upper() == "N":
            result = 0
        return result

    # Function untuk menampilkan menu
    def menu():
        os.system("cls")
        print("+-------------+--------------+-------------+")
        print("|     WELCOME TO SMTOWN CONCERT CENTER     |")
        print("+-------------+--------------+-------------+")
        print("")
        t = PrettyTable(['No', 'Menu'])
        t.add_row(['1', 'Schedule Live Update'])
        t.add_row(['2', 'Show Concert Schedule'])
        t.add_row(['3', 'Buy Ticket'])
        t.add_row(['4', 'My SMTown Ticket'])
        t.add_row(['5', 'Back'])
        t.align = 'l'
        print(t)
    
    # Main function
    def main():
        # Membuat objek client MQTT
        client = mqtt.Client()  

        # Client membuat koneksi dengan broker
        client.on_connect = on_connect
        client.connect("broker.hivemq.com", 1883)

        # Mendefinisikan pesan berbentuk dictionary yang berisi key dan value untuk di-publish
        to_publish = ({
            "client": "User",
            "name": username,
            "code": "Subs", 
            "destination": "SMTown",
        })
        # Mengkonversi dictionary menjadi string dalam format JSON 
        to_publish_json = json.dumps(to_publish)
        client.publish("user", to_publish_json)

        # Client meng-subscribe topik dari Publisher SMTown
        client.subscribe("korean_ballad")

        # Memanggil callback on_message
        client.on_message = on_message

        # Membuat objek cursor untuk 'usernamepassword.db'
        cursor2 = conn2.cursor()

        # Mengecek apakah sudah terdapat table bernama 'smtown' pada 'usernamepassword.db'
        cursor2.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='smtown'")

        # Mendapatkan hasil dari query dengan kondisi yang dicari
        result2 = cursor2.fetchone()

        # Jika belum ada, akan dibuat table bernama 'smtown'
        if result2 is None:
            cursor2.execute("CREATE TABLE smtown (title TEXT, date TEXT, time TEXT, seat TEXT, quantity INTEGER)")
            conn2.commit()

        # Client memulai loop
        client.loop_start()

        #client.on_message = on_message

        while True:

            # Menampilkan menu
            menu()

            choice = input("Enter your choice: ")

            # Jika '1' berarti untuk melihat live update jadwal konser 
            if choice == "1":
                global to_print 

                to_print = True
                while True:
                    os.system('cls')
                    print("+------------+-------------+------------+")
                    print("|         SCHEDULE LIVE UPDATE          |")
                    print("+------------+-------------+------------+")
                    print("\nPress 'Q' to return to the previous menu\n")

                    # Menampilkan semua pesan yang diterima
                    display_messages()
                    
                    if input().upper() == "Q":
                        to_print = False
                        break
      
            # Jika '2' berarti untuk melihat jadwal lengkap konser dalam tabel
            elif choice == "2":
                while True:
                    os.system('cls')
                    while True:
                        os.system("cls")
                        print("+-------------+--------------+-------------+")
                        print("|          MGWTON CONCERT SCHEDULE         |")
                        print("+-------------+--------------+-------------+\n")

                        # Membuat tabel 
                        table = PrettyTable(["Title", "Date", "Time", "Performers"])

                        # Memanggil function show_schedule untuk membuat tabel berdasarkan pesan yang telah diterima (code == 'Add' / 'Delete')
                        show_schedule(sm_concerts, table)

                        # Mencetak table
                        print(table)

                        choice = input("Press 'Enter' to update a schedule, Press 'Q' to return to previous menu: ")
                        if choice.upper() == 'Q':
                            break
                    break

            # Jika '3' berarti untuk mem-booking tiket
            elif choice == "3":
                while True:
                    os.system("cls")
                    ticket_class = ["Silver", "Gold", "Platinum", "Diamond"]
                    print("+-------------+--------------+-------------+")
                    print("|                BUY TICKET                |")
                    print("+-------------+--------------+-------------+\n")

                    # Menampilkan jadwal lengkap konser
                    table = PrettyTable(["Title", "Date", "Time", "Performers"])
                    show_schedule(sm_concerts, table)
                    print(table)
                    print("")

                    # Menampilkan list harga
                    t = PrettyTable(field_names=ticket_class)
                    t.add_row(['1.250.000', '1.750.000', '2.500.000', '3.250.000'])
                    print(t)
                    print("")

                    # Mendapatkan data konser yang akan dibooking
                    concert_title = input("Concert title: ")
                    seat_plan = input("Seat plan: ")
                    while True:
                        try:
                            quantity = int(input("Quantity (Maximum 5): "))
                            break
                        except ValueError:
                            print("Value for quantity must be integer. Try again ...")

                    price = 0
                    print("") 

                    if (seat_plan == ticket_class[0]):
                        price = quantity * 1250000
                    elif (seat_plan == ticket_class[1]):
                        price = quantity * 1750000
                    elif (seat_plan == ticket_class[2]):
                        price = quantity * 2500000
                    elif (seat_plan == ticket_class[3]):
                        price = quantity * 3250000
                    
                    if (concert_title == "" or concert_title not in [concert['title'] for concert in sm_concerts] or
                        seat_plan not in ticket_class or 
                        quantity < 1 or quantity > 5):
                        print("There is an invalid input, want to try again? (y/n): ")
                        if input().upper() == "N":
                            break
                    else:
                        choice2 = input("Submit your concert plan (y/n): ")
                        if choice2.upper() == "Y":
                            if advance_ticketing(cursor2, concert_title, seat_plan, quantity, price, client) == 1:
                                break
                            else:
                                pass
                        elif choice2.upper() == "N":
                            print("\nPress 'B' to buy, Press 'Q' to return to previous menu: ")
                            if input().upper() == "Q":
                                break
            
            # Jika '4' berarti untuk menampilkan tiket SMTown yang telah dibooking
            elif choice == "4":
                while True:
                    os.system("cls")
                    print("+-------------+--------------+-------------+")
                    print("|            MY SMTOWN TICKETS             |")
                    print("+-------------+--------------+-------------+\n")
                    
                    # Kondisi untuk mengambil semua row yang berada di table smtown
                    cursor2.execute("SELECT * FROM smtown")

                    # Mengambil semua row dengan kondisi yang telah ditentukan 
                    rows = cursor2.fetchall()

                    # Iterasi melalui rows untuk mencetak value dari setiap kolom dari setiap row
                    for row in rows:
                        print("Concert title :", row[0])
                        print("Date          :", row[1])
                        print("Time          :", row[2])
                        print("Seat plan     :", row[3])
                        print("Quantity      :", row[4])
                        print("")

                    print("\nPress 'Q' to return to previous menu: ")
                    if input().upper() == "Q":
                            break

            # Jika '5' berarti kembali ke main menu
            elif choice == "5":
                client.loop_stop()
                break

    if __name__ == "__main__":
        main()

# Function yang menampung program YG
def YG():

    # Callback ketika client terhubung dengan broker
    def on_connect(client, userdata, flags, rc):
        time.sleep(1.5)
    
    # Function untuk menginterpretasikan message untuk dimasukkan ke dalam beberapa variabel
    def msg_interpreter(msg):
        # Menambahkan message yang berbentuk dictionary ke list 'yg_concerts'
        yg_concerts.append(msg)

        code = msg["code"]
        title = msg["title"]
        date = msg["date"]
        time = msg["time"]
        performers = msg["performers"]
        # Mengembalikan value dari masing-masing variabel
        return (code, title, date, time, performers)

    # Callback ketika client menerima pesan
    def on_message(client, userdata, msg):
        # Decode message dari bytes ke string
        message = msg.payload.decode()  
        # Mengkonversi message yang diterima (string JSON) ke dalam bentuk dictionary kembali
        data = json.loads(message)
        # Variabel untuk menampung kembalian dari function msg_interpreter()
        code, title, date, time, performers = msg_interpreter(data)

        current_time = datetime.now().strftime('%H:%M:%S')
        # Jika code == 'Add' berarti publisher telah menambahkan jadwal
        if (code == "Add"):
            psn = "[ YG ENT. NEW ADDED SCHEDULE | " + current_time + " ]\n" + "Title :  " + title + "\nDate :  " + date + "\nTime :  " + time + "\nPerformers :  " + performers + "\n"
        # Jika code == 'Delete' berarti publisher telah menghapus/cancel jadwal
        elif (code == "Delete"):
            psn = "[ YG ENT. CANCELED SCHEDULE | " + current_time + " ]\n" + "Title :  " + title + "\nDate :  " + date + "\nTime :  " + time + "\nPerformers :  " + performers + "\n"

        # menambahkan message/pesan/psn ke dalam list 
        yg_messages.append(psn)
        yg_unread_messages.append(psn)

        if to_print:
            print(psn)
    
    # Function untuk display semua message yang telah diterima
    def display_messages():
        # Print semua message dalam list
        for message in yg_messages:
            print(message)
  
        # Mengosongkan list unread_messages (berarti semua pesan telah dilihat/dibaca)
        yg_unread_messages = []
    
    # Function untuk membuat/meng-update table jadwal lengkap konser dengan parameter list concert dan table
    def show_schedule(concert, table):
        for concert in yg_concerts:
            # Jika code == 'Add' berarti menambahkan row
            if concert["code"] == "Add":
                title = concert["title"]
                date = concert["date"]
                time = concert["time"]
                performers = concert["performers"]
                table.add_row([title, date, time, performers])
            # Jika code == 'Delete' berarti menghapus row
            elif concert["code"] == "Delete":
                for i, row in enumerate(table._rows):
                    if row[0] == concert["title"]:
                        index = i
                        break
                # Jika row ditemukan, hapus row tersebut
                if index is not None:
                        table.del_row(index)
    
    # Function untuk menampilkan detail booking tiket
    def purchase_detail(table):
        os.system("cls")
        print("+-------------+--------------+-------------+")
        print("|              BOOKING SUCCESS             |")
        print("+-------------+--------------+-------------+\n")
        print(table)
        current_date = datetime.date(datetime.now())
        current_time = datetime.now().strftime('%H:%M:%S')
        print("Date and time of booking:", current_date, current_time)

        print("\nPress 'Q' to return to the main menu\n")
        if input().upper() == "Q":
                pass
        
    # Function untuk halaman konfirmasi booking tiket dengan salah satu parameternya adalah cursor untuk mengoperasikan/mengeksekusi database 
    def advance_ticketing(cursor2, concert_title, seat_plan, quantity, price, client):
        os.system("cls")
        print("+-------------+--------------+-------------+")
        print("|               CONFIRMATION               |")
        print("+-------------+--------------+-------------+\n")

        # Membuat table detail konser yang dibeli
        t = PrettyTable(['Title', 'Date', 'Time', 'Performers'])
        for concert in yg_concerts:
            if concert["title"] == concert_title:
                title = concert["title"]
                date = concert["date"]
                time = concert["time"]
                performers = concert["performers"]
                t.add_row([title, date, time, performers])
        print(t)
        print("")

        # Membuat table detail tiket konser yang akan di-booking
        t2 = PrettyTable(['Object', 'Detail'])
        t2.add_row(['Username', username])
        t2.add_row(['Concert title', concert_title])
        t2.add_row(['Seat plan', seat_plan])
        t2.add_row(['Quantity', quantity])
        t2.add_row(['Total price', price])
        t2.align = 'l'
        print(t2)
        print("")

        # Mendefinisikan pesan berbentuk dictionary yang berisi key dan value untuk di-publish
        to_publish = ({
            "client": "User",
            "name": username,
            "code": "Book", 
            "destination": "YG Entertainment",
        })
        # Mengkonversi dictionary menjadi string dalam format JSON 
        to_publish_json = json.dumps(to_publish)

        result = 0
        confirm = input("Confirm your booking (y/n): ")
        if confirm.upper() == "Y":
            # Menambahkan row ke table dengan value konser yang telah dibooking
            cursor2.execute("INSERT INTO yg_ent (title, date, time, seat, quantity) VALUES (?, ?, ?, ?, ?)", (concert_title, date, time, seat_plan, quantity))
            conn2.commit()
            # Publish pesan
            client.publish("user", to_publish_json)
            purchase_detail(t2)
            result = 1
        elif confirm.upper() == "N":
            result = 0
        return result

    # Function untuk menampilkan menu
    def menu():
        os.system("cls")
        print("+-------------+--------------+--------------+")
        print("|     WELCOME TO YG ENT. CONCERT CENTER     |")
        print("+-------------+--------------+--------------+")
        print("")
        t = PrettyTable(['No', 'Menu'])
        t.add_row(['1', 'Schedule Live Update'])
        t.add_row(['2', 'Show Concert Schedule'])
        t.add_row(['3', 'Buy Ticket'])
        t.add_row(['4', 'My YG Entertainment Ticket'])
        t.add_row(['5', 'Back'])
        t.align = 'l'
        print(t)
    
    # Main function
    def main():
        # Membuat objek client MQTT
        client = mqtt.Client()  

        # Client membuat koneksi dengan broker
        client.on_connect = on_connect
        client.connect("broker.hivemq.com", 1883)

        # Mendefinisikan pesan berbentuk dictionary yang berisi key dan value untuk di-publish
        to_publish = ({
            "client": "User",
            "name": username,
            "code": "Subs", 
            "destination": "YG Entertainment",
        })
        # Mengkonversi dictionary menjadi string dalam format JSON 
        to_publish_json = json.dumps(to_publish)
        client.publish("user", to_publish_json)

        # Client meng-subscribe topik dari Publisher YG Entertainment
        client.subscribe("girlband")

        # Memanggil callback on_message
        client.on_message = on_message

        # Membuat objek cursor untuk 'usernamepassword.db'
        cursor2 = conn2.cursor()

        # Mengecek apakah sudah terdapat table bernama 'yg_ent' pada 'usernamepassword.db'
        cursor2.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='yg_ent'")

        # Mendapatkan hasil dari query dengan kondisi yang dicari
        result2 = cursor2.fetchone()

        # Jika belum ada, akan dibuat table bernama 'yg_ent'
        if result2 is None:
            cursor2.execute("CREATE TABLE yg_ent (title TEXT, date TEXT, time TEXT, seat TEXT, quantity INTEGER)")
            conn2.commit()


        # Client memulai loop
        client.loop_start()

        while True:
            # Menampilkan menu
            menu()

            choice = input("Enter your choice: ")

            # Jika '1' berarti untuk melihat live update jadwal konser 
            if choice == "1":
                global to_print
                to_print = True
                while True:
                    os.system('cls')
                    print("+------------+-------------+------------+")
                    print("|         SCHEDULE LIVE UPDATE          |")
                    print("+------------+-------------+------------+")
                    print("\nPress 'Q' to return to the previous menu\n")

                    # Menampilkan semua pesan yang diterima
                    display_messages()

                    if input().upper() == "Q":
                        to_print = False
                        break
      
            # Jika '2' berarti untuk melihat jadwal lengkap konser dalam tabel
            elif choice == "2":
                while True:
                    os.system('cls')
                    while True:
                        os.system("cls")
                        print("+-------------+--------------+--------------+")
                        print("|          YG ENT. CONCERT SCHEDULE         |")
                        print("+-------------+--------------+--------------+\n")

                        # Membuat tabel 
                        table = PrettyTable(["Title", "Date", "Time", "Performers"])

                        # Memanggil function show_schedule untuk membuat tabel berdasarkan pesan yang telah diterima (code == 'Add' / 'Delete')
                        show_schedule(yg_concerts, table)

                        # Mencetak table
                        print(table)

                        choice = input("Press 'Enter' to update a schedule, Press 'Q' to return to previous menu: ")
                        if choice.upper() == 'Q':
                            break
                    break

            # Jika '3' berarti untuk mem-booking tiket
            elif choice == "3":
                while True:
                    os.system("cls")
                    ticket_class = ["Silver", "Gold", "Platinum", "Diamond"]
                    print("+-------------+--------------+-------------+")
                    print("|                BUY TICKET                |")
                    print("+-------------+--------------+-------------+\n")

                    # Menampilkan jadwal lengkap konser
                    table = PrettyTable(["Title", "Date", "Time", "Performers"])
                    show_schedule(yg_concerts, table)
                    print(table)
                    print("")

                    # Menampilkan list harga
                    t = PrettyTable(field_names=ticket_class)
                    t.add_row(['1.250.000', '1.750.000', '2.500.000', '3.250.000'])
                    print(t)
                    print("")

                    # Mendapatkan data konser yang akan dibooking
                    concert_title = input("Concert title: ")
                    seat_plan = input("Seat plan: ")
                    quantity = int(input("Quantity (Maximum 5): "))
                    price = 0
                    print("")

                    if (seat_plan == ticket_class[0]):
                        price = quantity * 1250000
                    elif (seat_plan == ticket_class[1]):
                        price = quantity * 1750000
                    elif (seat_plan == ticket_class[2]):
                        price = quantity * 2500000
                    elif (seat_plan == ticket_class[3]):
                        price = quantity * 3250000
                    
                    if (concert_title not in [concert['title'] for concert in yg_concerts] or
                        seat_plan not in ticket_class or
                        quantity > 5):
                        print("There is an invalid input, want to try again? (y/n): ")
                        if input().upper() == "N":
                            break
                    else:
                        choice2 = input("Submit your concert plan (y/n): ")
                        if choice2.upper() == "Y":
                            if advance_ticketing(cursor2, concert_title, seat_plan, quantity, price, client) == 1:
                                break
                            else:
                                pass
                        elif choice2.upper() == "N":
                            print("\nPress 'B' to buy, Press 'Q' to return to previous menu: ")
                            if input().upper() == "Q":
                                break
            
            # Jika '4' berarti untuk menampilkan tiket YG Entertainment yang telah dibooking
            elif choice == "4":
                while True:
                    os.system("cls")
                    print("+-------------+--------------+--------------+")
                    print("|            MY YG ENT. TICKETS             |")
                    print("+-------------+--------------+--------------+\n")
                    
                    # Kondisi untuk mengambil semua row yang berada di table yg_ent
                    cursor2.execute("SELECT * FROM yg_ent")

                    # Mengambil semua row dengan kondisi yang telah ditentukan 
                    rows = cursor2.fetchall()

                    # Iterasi melalui rows untuk mencetak value dari setiap kolom dari setiap row
                    for row in rows:
                        print("Concert title :", row[0])
                        print("Date          :", row[1])
                        print("Time          :", row[2])
                        print("Seat plan     :", row[3])
                        print("Quantity      :", row[4])
                        print("")

                    print("\nPress 'Q' to return to previous menu: ")
                    if input().upper() == "Q":
                            break

            # Jika '5' berarti kembali ke main menu
            elif choice == "5":
                client.loop_stop()
                break

    if __name__ == "__main__":
        main()

def main_menu():
    os.system("cls")
    print("+-------------+--------------+--------------+")
    print("|   WELCOME TO THE AGENCIES CONCERT CENTRE  |")
    print("+-------------+--------------+--------------+\n")

    t = PrettyTable(['No', 'Menu'])
    t.add_row(['1', 'SMTown (korean ballad)'])
    t.add_row(['2', 'YG Entertainment (girlband)'])
    t.add_row(['3', 'My Ticket'])
    t.add_row(['4', 'Exit'])
    t.align = 'l'
    print(t)

while True:
    os.system("cls")

    # Menampilkan menu
    main_menu()

    choice = input("Enter your choice: ")

    if choice == "1":
        SMTown()
    
    elif choice == "2":
        YG()
    
    elif choice == "3":
        while True:
            os.system("cls")
            print("+-------------+--------------+--------------+")
            print("|                MY TICKETS                 |")
            print("+-------------+--------------+--------------+\n")

            # Membuat objek cursor untuk 'usernamepassword.db'
            cursor3 = conn2.cursor()
            cursor4 = conn2.cursor()

            cursor3.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='smtown'")
            result3 = cursor3.fetchone()
            if result3 is None:
                cursor3.execute("CREATE TABLE smtown (title TEXT, date TEXT, time TEXT, seat TEXT, quantity INTEGER)")
                conn2.commit

            cursor4.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='yg_ent'")
            result4 = cursor4.fetchone()
            if result4 is None:
                cursor4.execute("CREATE TABLE yg_ent (title TEXT, date TEXT, time TEXT, seat TEXT, quantity INTEGER)")
                conn2.commit()
            
            # Kondisi untuk mengambil semua row yang berada di table yg_ent
            cursor3.execute("SELECT * FROM smtown")
            cursor4.execute("SELECT * FROM yg_ent")

            # Mengambil semua row dengan kondisi yang telah ditentukan 
            rows1 = cursor3.fetchall()
            rows2 = cursor4.fetchall()

            print("[ SMTown Ticket ]")
            # Iterasi melalui rows untuk mencetak value dari setiap kolom dari setiap row
            for row in rows1:
                print("Concert title :", row[0])
                print("Date          :", row[1])
                print("Time          :", row[2])
                print("Seat plan     :", row[3])
                print("Quantity      :", row[4])
                print("")
            
            print("\n[ YG Entertainment Ticket ]")
            # Iterasi melalui rows untuk mencetak value dari setiap kolom dari setiap row
            for row in rows2:
                print("Concert title :", row[0])
                print("Date          :", row[1])
                print("Time          :", row[2])
                print("Seat plan     :", row[3])
                print("Quantity      :", row[4])
                print("")
            
            print("\nPress 'Q' to return to previous menu: ")
            if input().upper() == "Q":
                    break
    
    elif choice == "4":
        os.system("cls")
        break
