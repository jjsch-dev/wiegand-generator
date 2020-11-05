"""MC-100 wiegand generator utility.
   It is used to generate card identifiers with the MC-100 converter in wiegand format.
   0 to 255 for the facility code and 0 to 65535 for the user identifier.
   The output format can be standard 26-bit or mifare 32-bit.
   The MC-100 converter must be configured for CDC serial input and wiegand output.
   NOTE: for generate win32 use: WINEARCH=win32 WINEPREFIX=~/win32 wine pyinstaller.exe --onefile xml_datetime.py
      for run win32: WINEARCH=win32 WINEPREFIX=~/win32 sudo wine ./xml_datetime.exe

"""

import serial
import argparse
import time
import platform
import os

parser = argparse.ArgumentParser(description="wiegand generator for MC-100")
parser.add_argument('--version', action='version', version='%(prog)s 0.1.4')
parser.add_argument("-p", "--port", required=True, help="serial communication port (win = COMxxx, linux = ttyXXXX, file = *.txt)")
parser.add_argument("-o", "--output", type=str, required=True, help="specify the output string format, std26 = wiegand 26-bit standard, mif32 = mifare 32-bit.")
parser.add_argument("-f", "--facility", type=int, required=True, help="0 to 255")
parser.add_argument("-i", "--identifier", type=int, required=True, help="0 to 65535")
parser.add_argument("-c", "--count", type=int, required=True, help="times the identifier increments")
parser.add_argument("-d", "--delay", type=int, required=True, help="delay in mS between identifiers")
args = parser.parse_args()

id_len = 0
is_serial = True


def check_params():
    global id_len, is_serial

    file_name, file_extension = os.path.splitext(args.port)

    is_serial = False if file_extension == '.txt' else True

    if 'std26' == args.output:
        id_len = 0xFFFF
    elif 'mif32' == args.output:
        id_len = 0xFFFFFFFF
    else:
        return False

    if 0 > args.facility > 255:
        return False

    if 0 > args.identifier > id_len:
        return False

    return True


def open_port():
    if is_serial:
        try:
            return serial.Serial(args.port, "115200", 8, 'N', 1, timeout=1)
        except:
            return None
    else:
        try:
            return open(args.port, 'w')
        except FileNotFoundError:
            return None


def close_port(serial_device):
    try:
        serial_device.close()
    except: pass


def generate_codes(serial_device):
    global id_len

    count = args.count

    for fc in range(args.facility, 255):
        for identifier in range(args.identifier, id_len):

            if args.output == 'std26':
                card_id = "{:03d}{:04d}".format(fc, identifier)
            else:
                card_id = "{:010d}".format(identifier)

            send_id = card_id + "\n\r"

            try:
                if is_serial:
                    serial_device.write(send_id.encode(encoding='ascii'))
                else:
                    serial_device.write(card_id + "\n")
                print(card_id)
            except:
                print("{} {} write error".format(card_id,
                                                 'serial' if is_serial else 'file'))

            if not count:
                return
            count -= 1

            time.sleep(args.delay/1000)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("\nos: {} - arch: {} - cpu: {}\n".format(platform.system(),
                                                   platform.architecture(),
                                                   platform.processor()))
    if check_params():
        device = open_port()
        if device:
            generate_codes(device)
            close_port(device)
        else:
            print("Can't open the {}".format('serial port' if is_serial else 'file'))
    else:
        parser.print_help()
