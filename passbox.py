import sqlite3

run = True

while run:
    print("\n\n\nMenu:\nSelect Action")
    action = int(input("[1] Enter a new username and password\n[2] Browse entries\n[3] Remove an entry\n[4] Quit\n"))
    
    if action==1:
        print("Create new entry:\nPress enter to return to menu\n")
        purpose = input("Input entry name:\n")
        
        if purpose == "":
            continue
        
        username = input("\nInput username:\n")
        password = input("\nInput password:\n")
        
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO entries (purpose, username, password) VALUES (?, ?, ?)", (purpose, username, password))

        
        connection.commit()
        cursor.close()
        connection.close()
    elif action==2:
        print("Select entry to view by entering id:\nPress enter to return to menu\n")
        
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        
        for row in cursor.execute("SELECT id, purpose FROM entries"):
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
            print("Entry with purpose '{}' not found.".format(selection))
        
        cursor.close()
        connection.close()
        
        input("\nPress enter to continue")
    elif action ==3:
        print("\nSelect entry to remove by entering id:\nPress enter to return to menu\n1")
        
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        
        for row in cursor.execute("SELECT id, purpose FROM entries"):
            print(f"[{row[0]}] {row[1]}")
        selection = input("\n")     
        
        if selection == "":
            continue
        
        cursor.execute("DELETE FROM entries WHERE id = ?", (selection,))
        connection.commit()
        
        cursor.close()
        connection.close()      
        
        input("Entry removed\nPress enter to continue")
    else:
        run=False

