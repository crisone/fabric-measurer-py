import os
import json
from struct import pack, unpack
from datetime import datetime

from terminaltables import AsciiTable
from mock_sender import SERIAL_PORT

# from protocol import Communicator
from protocol_simple import Communicator


def read_config():
    serial_port = '/dev/cu.usbserial-14220'
    baudrate = 115200

    try:
        cfg = json.load(open(".config.json"))
        serial_port = cfg["serial_port"]
        baudrate = cfg["baudrate"]
    except:
        pass

    s = input("请输入串口设备号({}):".format(serial_port))
    if s:
        serial_port = s

    b = input("请输入串口波特率({}):".format(baudrate))
    if b:
        baudrate = b

    json.dump({
        "serial_port": serial_port,
        "baudrate": baudrate
    }, open(".config.json", "w"))

    return serial_port, baudrate


def do_recv():
    serial_port, baudrate = read_config()
    c = Communicator(serial_port, baudrate)

    log_file = "{}.txt".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
    with open(log_file, "w") as f:
        while True:
            p = c.recv()
            ts = unpack('>256H', p.payload)

            tdata = [
                [pack('B', 65 + i).decode() for i in range(16)]
            ]
            for r in range(16):
                tdata.append(
                    ts[r*16: (r+1)*16]
                )

            table = AsciiTable(tdata)
            if os.name == "nt":
                os.system("cls")
            else:
                os.system("clear")
            print(c.get_stats())
            print(table.table)
            f.write(",".join([str(d) for d in ts]))
            f.write("\n")


if __name__ == "__main__":
    do_recv()
