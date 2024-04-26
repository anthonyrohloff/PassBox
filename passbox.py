import sqlite3
import getpass
import os
import secrets
import string
import random

# Only skip login after first-time setup
skip_login = False

# Database file path
db = "credentials.db"

# Check if the database file exists
if not os.path.exists(db):
    # If the database file doesn't exist, create it and perform initial setup
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    # Create all necessary tables
    cursor.execute("CREATE TABLE setup(master TEXT)")
    cursor.execute("CREATE TABLE entries(id INTEGER PRIMARY KEY AUTOINCREMENT, service TEXT, username TEXT, password TEXT)")
    connection.commit()

    # Set master password
    setup_loop = True
    while setup_loop:
        # User enters password twice
        password1 = getpass.getpass("\nEnter master password: ")
        password2 = getpass.getpass("\nRe-enter master password: ")
        
        # If passwords match, set master password
        if password1 == password2:
            cursor.execute("INSERT INTO setup (master) VALUES (?)", (password1,))
            connection.commit()
            setup_loop = False
            skip_login = True
        # Else, try again
        else:
            print("Passwords do not match!\nTry again\n")
            continue

    # Close the connection
    cursor.close()
    connection.close()

# Login loop
login = False
while not login and not skip_login:
    master = getpass.getpass("\nEnter master password: ")
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("SELECT master FROM setup")
    fetched_master = cursor.fetchone()
    
    # If entered password matches db, access granted
    if fetched_master and master == fetched_master[0]:
        print(("Access Granted"))
        login = True
    # Else, try again
    else:
        print("Access Denied\nTry again")
    
    # Close the connection
    cursor.close()
    connection.close()

# Main loop
run = True
skip_menu = False
while run:
    if not skip_menu:
        print("\n\n\nMenu:\nSelect Action")
        action = int(input("[1] Create new entry\n[2] Browse entries\n[3] Remove an entry\n[4] Quit\n"))
    else:
        skip_menu = False
        
    # Create a new entry
    if action==1:
        print("Create new entry:\nPress enter to return to menu\n")
        service = input("Input entry name:\n")
        
        if service == "":
            continue
        
        username = input("\nInput username:\n")
        
        generate = input("\nGenerate complex password? [y/n]: ")
        if generate == "y":
            accept = "n"
            while accept == "n":
                length = int(input("\nEnter desired length of password: "))
                password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for x in range(length))  
                accept = input("\nYour password is: "+ str(password) + "\nAccept password? [y/n]: ")
        else:
            password = input("\nInput password:\n")
        
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO entries (service, username, password) VALUES (?, ?, ?)", (service, username, password))

        
        connection.commit()
        cursor.close()
        connection.close()
    # Browse entries
    elif action==2:
        print("Select entry to view by entering id:\nPress enter to return to menu\n")
        
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        
        for row in cursor.execute("SELECT id, service FROM entries"):
            print(f"[{row[0]}] {row[1]}")
        selection = input("\n")
        
        if selection == "":
            continue
        
        cursor.execute("SELECT * FROM entries WHERE id=?", (selection,))
        
        selected_entry = cursor.fetchone()
        
        if selected_entry:
            print(f"Entry for {selected_entry[1]}:")
            print("Username:", selected_entry[2])
            print("Password:", selected_entry[3])
        else:
            print("Entry with service '{}' not found.".format(selection))
        
        cursor.close()
        connection.close()
        
        input("\nPress enter to continue")
    # Remove an entry
    elif action ==3:
        print("\nSelect entry to remove by entering id:\nPress enter to return to menu\n")
        
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        
        print("[d] Delete all entries")
        for row in cursor.execute("SELECT id, service FROM entries"):
            print(f"[{row[0]}] {row[1]}")
        selection = input("\n")     
        
        if selection == "":
            continue
        elif selection == "d":
            confirm = input("Are you sure? This will DELETE ALL of your entries [y/n]: ")
            if confirm == "y":
                connection.commit()
                cursor.close()
                connection.close()    
                
                os.remove("credentials.db")
                print("\nAll data cleared\n")
                run = False
                
                continue
            else:
                action = 3
                skip_menu = True
                continue
                
        cursor.execute("DELETE FROM entries WHERE id = ?", (selection,))
        connection.commit()
        
        cursor.close()
        connection.close()      
        
        input("Entry removed\nPress enter to continue")
    # Quit
    else:
        run=False