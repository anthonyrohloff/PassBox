# Libraries
import sqlite3
import getpass
import os
import secrets
import string

# Files
from encryption import derive_encryption_key, encrypt_password, decrypt_password, hash_password
from logging import log_action

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
    cursor.execute("CREATE TABLE setup(master BLOB, key BLOB)")
    cursor.execute("CREATE TABLE entries(id INTEGER PRIMARY KEY AUTOINCREMENT, service TEXT, username TEXT, password BLOB)")
    cursor.execute("CREATE TABLE log(id INT, action TEXT, time TEXT)")
    connection.commit()

    # Set master password
    setup_loop = True
    while setup_loop:
        # User enters password twice
        password1 = getpass.getpass("\nEnter master password: ")
        password2 = getpass.getpass("\nRe-enter master password: ")
        
        # If passwords match, set master password
        if password1 == password2:
            master_hash = hash_password(password1)
            
            # Generate unique salt
            salt = os.urandom(32)
            # Generate key
            key = derive_encryption_key(password1, salt)
            
            cursor.execute("INSERT INTO setup (master, key) VALUES (?, ?)", (master_hash, key,))
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
login = False#
while not login and not skip_login:
    master = getpass.getpass("\nEnter master password: ")
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("SELECT master FROM setup")
    fetched_master = cursor.fetchone()
    
    # If entered password matches db, access granted
    if fetched_master and hash_password(master) == fetched_master[0]:
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
        try:
            print("\n\n\nMenu:\nSelect Action")
            action = input("[1] Create new entry\n[2] Browse entries\n[3] Remove an entry\n[4] View log\n[5] Quit\n")
            
            if action not in ["1", "2", "3", "4", "5"]:
                raise ValueError("\nPlease enter a valid menu option")
        except ValueError as e:
            print(e)
            continue
    else:
        skip_menu = False
        
    # Create a new entry
    if action=="1":
        print("Create new entry:\nPress enter to return to menu\n")
        service = input("Input entry name:\n")
        
        if service == "":
            continue
        
        username = input("\nInput username:\n")
        
        creating = True
        while creating:
            generate = input("\nGenerate complex password? [y/n]: ")
            try:
                if generate not in ["y", "n"]:
                    raise ValueError("Please enter a valid option")
                if generate == "y":
                    accept = "n"
                    
                    while accept == "n":
                        length = int(input("\nEnter desired length of password: "))

                        validated = False
                        while not validated:
                            password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for x in range(length))  
                            try:
                                accept = input("\nYour password is: "+ str(password) + "\nAccept password? [y/n]: ")
                                
                                if accept not in ["y", "n"]:
                                    raise ValueError("Please enter a valid input")
                                
                                validated = True
                                
                            except ValueError as e:
                                print(e)
                                continue
                            
                else:
                    password = input("\nInput password:\n")
                
                encrypted_password = encrypt_password(password)
                
                connection = sqlite3.connect(db)
                cursor = connection.cursor()
                cursor.execute("INSERT INTO entries (service, username, password) VALUES (?, ?, ?)", (service, username, encrypted_password))

                cursor.execute("SELECT MAX(id) FROM entries")
                entry_id = cursor.fetchone()[0]

                connection.commit()
                cursor.close()
                connection.close()
                
                log_action("Created", entry_id)

                creating = False
            except ValueError as e:
                print(e)
                continue
        
    # Browse entries
    elif action == "2":
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM entries")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("\nNo entries to view")
            continue
        
        print("Select entry to view by entering id:\nPress enter to return to menu\n")
    
        selecting = True
        while selecting:
            id_list = []
            for row in cursor.execute("SELECT id, service FROM entries"):
                print(f"[{row[0]}] {row[1]}")
                id_list.append(row[0])
            
            try:
                selection = int(input("\n"))

                if selection not in id_list and selection:
                    print("\nPlease enter a valid number\n")
                    continue
                selecting = False
                
            except:
                print("\nPlease enter a number\n")
                continue
        
        if selecting:
            continue
        
        if selection:
            cursor.execute("SELECT * FROM entries WHERE id=?", (selection,))

            selected_entry = cursor.fetchone()
            
            if selected_entry:
                print(f"Entry for {selected_entry[1]}:")
                print("Username:", selected_entry[2])
                
                selected_password = selected_entry[3]

                print("Password:", decrypt_password(selected_password))
            else:
                print("Entry with service '{}' not found.".format(selection))
            
            cursor.close()
            connection.close()

            log_action("Viewed", selection) 

            input("\nPress enter to continue")
        
    # Remove an entry
    elif action == "3":
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM entries")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("\nNo entries to remove")
            continue
        
        selecting = True
        while selecting:
            id_list = []

            print("\nSelect entry to remove by entering id:\nPress enter to return to menu\n")

            for row in cursor.execute("SELECT id, service FROM entries"):
                print(f"[{row[0]}] {row[1]}")
                id_list.append(str(row[0]))
            print("[d] Delete all entries")        
            
            selection = input("\n")     
            
            if selection not in id_list and selection != "d" and selection != "":
                print("Please enter a valid input")
                continue
            
            if selection in id_list:
                cursor.execute("DELETE FROM entries WHERE id = ?", (int(selection),))

                connection.commit()
                cursor.close()
                connection.close()      
            
                log_action("Removed", selection)

                input("Entry removed\nPress enter to continue")
                break
            elif selection == "d":
                deleting = False

                while not deleting:
                    confirmation = input("Are you sure? This will DELETE ALL entries. [y/n]\n")
                    if confirmation in ["y", "n"]:
                        if confirmation == "y":
                            deleting = True
                            selecting = False
                            pass
                        elif confirmation == "n":
                            break
                    else:
                        print("\nPlease enter a valid input\n")
                        continue

                    cursor.close()
                    connection.close()
                    os.remove("credentials.db")
                    run = False
                    break
            elif selection == '':
                selecting = False

    elif action == "4":
        print("\n")
        connection = sqlite3.connect(db)
        cursor = connection.cursor()        

        for row in cursor.execute("SELECT id, action, time FROM log"):
            print(f"{row[1]} entry with id {row[0]} at {row[2]}")    

        connection.commit()
        cursor.close()
        connection.close()   

        input("\nPress enter to continue")
        
    # Quit
    else:
        run=False