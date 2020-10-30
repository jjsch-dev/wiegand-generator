"""MC-100 wiegand generator utility.
   It is used to generate card identifiers with the MC-100 converter in wiegand 26 format.
   0 to 255 for the facility code and 0 to 65535 for the user identifier.
   The MC-100 converter must be configured for CDC serial input and wiegand output.
"""

import serial
import argparse
import time

parser = argparse.ArgumentParser(description="wiegand generator for MC-100")
parser.add_argument('--version', action='version', version='%(prog)s 0.1.2')
parser.add_argument("-p", "--port", required=True, help="serial communication port (win = COMxxx, linux = ttyXXXX)")
parser.add_argument("-f", "--facility", type=int, required=True, help="0 to 255")
parser.add_argument("-i", "--identifier", type=int, required=True, help="0 to 65535")
parser.add_argument("-c", "--count", type=int, required=True, help="times the identifier increments")
parser.add_argument("-d", "--delay", type=int, required=True, help="delay in mS between identifiers")
args = parser.parse_args()


def check_params():
    if 0 > args.facility > 255:
        return False

    if 0 > args.identifier > 65535:
        return False
    return True


def open_port():
    try:
        return serial.Serial(args.port, "115200", 8, 'N', 1, timeout=1)
    except:
        return None


def generate_codes(serial_device):
    count = args.count

    for fc in range(args.facility, 255):
        for identifier in range(args.identifier, 65535):
            card_id = "{:03d}{:04d}".format(fc, identifier)

            send_id = card_id + "\n\r"

            try:
                serial_device.write(send_id.encode(encoding='ascii'))
                print(card_id)
            except:
                print("{} serial write error".format(card_id))

            if not count:
                return
            count -= 1

            time.sleep(args.delay/1000)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if check_params():
        device = open_port()
        if device:
            generate_codes(device)
        else:
            print("Can't open the serial port")
    else:
        parser.print_help()
