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
import progressbar

parser = argparse.ArgumentParser(description="wiegand generator for MC-100 or file")
parser.add_argument('--version', action='version', version='%(prog)s 0.1.8')
parser.add_argument("-p", "--port", nargs='+', required=True, help="serial communication port (win = COMxxx, linux = ttyXXXX, file = *.txt, accept port list: com1 com2 ...)")
parser.add_argument("-o", "--output", type=str, required=True, help="specify the output string format, std26 = wiegand 26-bit standard, mif32 = mifare 32-bit.")
parser.add_argument("-f", "--facility", type=int, required=True, help="0 to 255")
parser.add_argument("-i", "--identifier", type=int, required=True, help="0 to 65535")
parser.add_argument("-c", "--count", type=int, required=True, help="times the identifier increments")
parser.add_argument("-d", "--delay", type=int, required=True, help="delay in mS between identifiers")
parser.add_argument("-t", "--port_delay", type=int, help="delay in uS between ports", default=0)
args = parser.parse_args()

id_len = 0
is_serial = True


def check_params():
    global id_len, is_serial

    file_name, file_extension = os.path.splitext(args.port[0])

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
            devices = []
            for port in args.port:
                devices.append(serial.Serial(port, "115200", 8, 'N', 1, timeout=1))

            return devices
        except:
            return None
    else:
        try:
            return open(args.port[0], 'w')
        except FileNotFoundError:
            return None
        except PermissionError:
            return None


def close_port(devices):
    try:
        for serial_device in devices:
            serial_device.close()
    except: pass


def generate_codes(devices):
    global id_len

    count = 0

    print("{} {} "
          "identifiers in {} format "
          "starting at facility : {} "
          "and identifier : {}\n".format("send by serial" if is_serial else "generates a file of",
                                         args.count, args.output, args.facility, args.identifier))

    bar = progressbar.ProgressBar(max_value=args.count, prefix='send serial' if is_serial else 'made file ')
    bar.start(init=True)

    for fc in range(args.facility, 255):
        for identifier in range(args.identifier, id_len):
            id_delay_ms = args.delay
            if args.output == 'std26':
                card_id = "{:03d}{:05d}".format(fc, identifier)
            else:
                card_id = "{:010d}".format(identifier)

            send_id = card_id + "\n\r"

            try:
                if is_serial:
                    for index, serial_device in enumerate(devices):
                        serial_device.write(send_id.encode(encoding='ascii'))
                        if index == 0:
                            time.sleep(args.port_delay/1000000)
                            id_delay_ms -= args.port_delay/1000
                else:
                    devices[0].write(card_id + "\n")

                bar.update(count)
            except:
                print("{} {} write error".format(card_id,
                                                 'serial' if is_serial else 'file'))

            count += 1

            if args.count <= count:
                bar.finish()
                return

            time.sleep(id_delay_ms/1000)
    bar.finish()


# Main script.
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
