import bcrypt
import os

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
USER_DATA_FILE = BASE_DIR / "users.txt"

def hash_password(plain_text_password):
    password_bytes = plain_text_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_text_password, hashed_password):
    try:
        password_bytes = plain_text_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except ValueError:
        return False

def user_exists(username):
    if not os.path.exists(USER_DATA_FILE):
        return False
        
    with open(USER_DATA_FILE, 'r') as f:
        for line in f:
            try:
                stored_username = line.strip().split(',', 1)[0]
                if stored_username == username:
                    return True
            except IndexError:
                continue 
    return False

def register_user(username, password):
    if user_exists(username):
        print(f"Error: Username '{username}' already exists.")
        return False
        
    hashed_pass = hash_password(password)
    
    with open(USER_DATA_FILE, 'a') as f:
        f.write(f"{username},{hashed_pass}\n")
        
    print(f"Success: User '{username}' registered successfully!")
    return True

def login_user(username, password):
    if not os.path.exists(USER_DATA_FILE):
        print("Error: Username not found.")
        return False
        
    with open(USER_DATA_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            try:
                stored_username, stored_hash = line.split(',', 1)
            except ValueError:
                continue
            
            if stored_username == username:
                if verify_password(password, stored_hash):
                    print(f"Success: Welcome, {username}!")
                    return True
                else:
                    print("Error: Invalid password.")
                    return False
                    
    print("Error: Username not found.")
    return False

def validate_username(username): 
    return True, ""

def validate_password(password):
    return True, ""

def display_menu():
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n [1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

def main():
    print("\nWelcome to the Week 7 Authentication System!")
    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()
        
        if choice == '1':
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
                
            password = input("Enter a password: ").strip()
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
                
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue
                
            register_user(username, password)
            
        elif choice == '2':
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()
            
            if login_user(username, password):
                print("\nYou are now logged in.")
                print("(In a real application, you would now access the protected data)")
                input("\nPress Enter to return to main menu...")
            
        elif choice == '3':
            print("\nThank you for using authentication system.")
            print("Exiting...")
            break
            
        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()