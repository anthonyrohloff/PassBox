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
while run:
    # Display menu
    try:
        print("\n\n\nMenu:\nSelect Action")
        action = input("[1] Create new entry\n[2] Browse entries\n[3] Remove an entry\n[4] View log\n[5] Quit\n")
        
        if action not in ["1", "2", "3", "4", "5"]:
            raise ValueError("\nPlease enter a valid menu option")
    
    # User did not enter a valid menu option
    except ValueError as e:
        print(e)
        continue
     
    # Create a new entry
    if action=="1":
        print("Create new entry:\nPress enter to return to menu\n")
        service = input("Input entry name:\n")
        
        # Enables returning to main menu upon pressing enter
        if service == "":
            continue
        
        username = input("\nInput username:\n")

        # Loop for generating password
        creating = True
        while creating:
            generate = input("\nGenerate complex password? [y/n]: ")

            # Add new entry
            try:
                if generate not in ["y", "n"]:
                    raise ValueError("Please enter a valid option")
                if generate == "y":
                    accept = "n"
                    
                    # Loop for generating new passwords until one is accepted
                    while accept == "n":
                        length = int(input("\nEnter desired length of password: "))

                        # Loop for accepting the password
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
                
                # Do not generate a password, enter one manually
                else:
                    password = input("\nInput password:\n")
                
                # Encrypt password
                encrypted_password = encrypt_password(password)
                
                connection = sqlite3.connect(db)
                cursor = connection.cursor()

                # Add entry into table
                cursor.execute("INSERT INTO entries (service, username, password) VALUES (?, ?, ?)", (service, username, encrypted_password))

                # Get id of entry
                cursor.execute("SELECT MAX(id) FROM entries")
                entry_id = cursor.fetchone()[0]

                connection.commit()
                cursor.close()
                connection.close()
                
                # Add action to log
                log_action("Created", entry_id)

                creating = False
            
            # User did not select y or n
            except ValueError as e:
                print(e)
                continue
        
    # Browse entries
    elif action == "2":
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        
        # Get number of entries
        cursor.execute("SELECT COUNT(*) FROM entries")
        count = cursor.fetchone()[0]
        
        # If number of entries is 0, go back to menu
        if count == 0:
            print("\nNo entries to view")
            continue
        
        print("Select entry to view by entering id:\nPress enter to return to menu\n")

        # Loop for selecting an entry to view
        selecting = True
        while selecting:
            
            # Init empty list to get all ids in table
            id_list = []
            
            # Print all entries
            for row in cursor.execute("SELECT id, service FROM entries"):
                print(f"[{row[0]}] {row[1]}")
                id_list.append(row[0])
            
            # Try to select an id
            try:
                selection = int(input("\n"))

                if selection not in id_list and selection:
                    print("\nPlease enter a valid number\n")
                    continue
                selecting = False
            
            # User did not input a valid id
            except:
                print("\nPlease enter a number\n")
                continue
        
        # View selection
        if selection:
            # Get all data from table where id's match
            cursor.execute("SELECT * FROM entries WHERE id=?", (selection,))

            selected_entry = cursor.fetchone()
            
            # Print out data
            print(f"Entry for {selected_entry[1]}:")
            print("Username:", selected_entry[2])
            
            selected_password = selected_entry[3]

            print("Password:", decrypt_password(selected_password))
            
            cursor.close()
            connection.close()

            # Log action
            log_action("Viewed", selection) 

            input("\nPress enter to continue")
        
    # Remove an entry
    elif action == "3":
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        
        # Count number of entries
        cursor.execute("SELECT COUNT(*) FROM entries")
        count = cursor.fetchone()[0]
        
        # If count is 0, there are no entries, continue
        if count == 0:
            print("\nNo entries to remove")
            continue
        
        # Loop for selecting entry to remove
        selecting = True
        while selecting:
            # Init empty list of ids
            id_list = []

            print("\nSelect entry to remove by entering id:\nPress enter to return to menu\n")

            # Print all entries in table and add to id_list
            for row in cursor.execute("SELECT id, service FROM entries"):
                print(f"[{row[0]}] {row[1]}")
                id_list.append(str(row[0]))
            print("[d] Delete all entries")        
            
            selection = input("\n")     
            
            # Check if selection was valid
            if selection not in id_list and selection != "d" and selection != "":
                print("Please enter a valid input")
                continue

            # If selection was an id, delete the id from the table
            if selection in id_list:
                cursor.execute("DELETE FROM entries WHERE id = ?", (int(selection),))

                connection.commit()
                cursor.close()
                connection.close()      

                # Log action
                log_action("Removed", selection)

                input("Entry removed\nPress enter to continue")
                break

            # If selection is d, reset app
            elif selection == "d":
                deleting = False

                # Loop for confirming deletion
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

    # View logged events
    elif action == "4":
        print("\n")
        connection = sqlite3.connect(db)
        cursor = connection.cursor()        

        # Print log table
        for row in cursor.execute("SELECT id, action, time FROM log"):
            print(f"{row[1]} entry with id {row[0]} at {row[2]}")    

        connection.commit()
        cursor.close()
        connection.close()   

        input("\nPress enter to continue")

    # Quit
    else:
        run=False