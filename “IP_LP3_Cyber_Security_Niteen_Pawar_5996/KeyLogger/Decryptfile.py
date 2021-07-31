from cryptography.fernet import Fernet

key="nLoJpSBIcrw9gJ_-yC5HNs-XIg2R7niyYFpwa0IulX0="

keys_information_e = "e_key_log.txt"
system_info_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"

encrypted_files = [system_info_e, keys_information_e, clipboard_information_e]
count = 0

for decrypting_file in encrypted_files:
    with open(encrypted_files[count],"rb") as f:
        data = f.read()

    fernet = Fernet(key)
    decrypted = fernet.decrypt(data)

    with open(encrypted_files[count],"wb") as f:
        f.write(decrypted)

    count += 1