import os
import json
from struct import pack, unpack
from datetime import datetime
import serial
import time

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


def decode_buf(data):
    i = 0
    # print("==========================================")
    # print(data['buf'].hex())
    while i + 1 < len(data['buf']):
        r, c = data['row'], data['col']

        v = data['buf'][i:i + 2]
        channel = v[0] >> 4
        val = (v[0] & 0x0F) * 256 + v[1]
        volt = 5 * val / 4095
        volt = round(volt * 1000)/1000

        if channel != r:
            # not right, reset
            print("reset")
            data['row'] = 15
            data['col'] = 0
            data['resets'] += 1
            i += 1
            continue

        # print(r, c, volt)
        data["mat"][r][c] = volt

        # every thing goes fine
        data['col'] += 1
        if data['col'] == 16:
            data['row'] += 1
            data['col'] = 0

        if data['row'] == 16:
            data['row'] = 0
            data['ready'] = True
            i += 2
            data["scans"] += 1
            break

        i += 2

    # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    data['recv_bytes'] += i
    data['buf'] = data['buf'][i:]


def decode_buf_single_line(data):
    i = 0
    while i + 1 < len(data['buf']):
        r, c = data['row'], data['col']

        v = data['buf'][i:i + 2]
        channel = v[0] >> 4
        val = (v[0] & 0x0F) * 256 + v[1]
        volt = 5 * val / 4095
        volt = round(volt * 1000)/1000

        # print("Channel {}, Volt {}".format(channel, volt))

        if channel != r:
            # not right, reset
            print("JUMP!!!!")
            # time.sleep(1)
            data['row'] = 14
            data['col'] = 0
            i += 1
            continue

        # print(r, c, volt)
        data["mat"][r][c] = volt

        # every thing goes fine
        data['col'] += 1
        if data['col'] == 16:
            # data['row'] += 1
            data['col'] = 0
            data['ready'] = True

        # if data['row'] == 16:
        #     data['row'] = 0
        #     data['ready'] = True
        #     i += 2
        #     data["scans"] += 1
        #     break

        i += 2

    data['recv_bytes'] += i
    data['buf'] = data['buf'][i:]


class Timer:
    def __init__(self, interval):
        self.interval = interval
        self.t = time.time()

    def ok(self):
        if time.time() - self.t > self.interval:
            self.t = time.time()
            return True
        else:
            return False


class FileSaver:
    def __init__(self, filename):
        self.file_h = open(filename, "w")

    def save(self, num):
        self.file_h.write("{}\n".format(num))

    def save_mat(self, mat):
        flats = []
        for row in mat:
            for c in row:
                flats.append(str(c))

        self.file_h.write(",".join(flats))
        self.file_h.write("\n")

    def close(self):
        self.file_h.close()


def do_recv_raw():
    serial_port, baudrate = read_config()
    s = serial.Serial(serial_port, baudrate, timeout=0.1)
    fs = FileSaver("data_log.txt")

    data = {
        "mat": [[0 for x in range(16)] for y in range(16)],
        "row": 0,
        "col": 0,
        "buf": b'',
        "ready": False,
        "recv_bytes": 0,
        "scans": 0,
        "resets": 0,
    }

    header = [[pack('B', 65 + i).decode() for i in range(16)]]
    tm = Timer(0.2)
    while True:
        bf = s.read(100)
        # print(bf.hex())
        data['buf'] += bf
        decode_buf(data)
        # decode_buf_single_line(data)
        # continue
        if data["ready"]:
            # fs.save(data["mat"][14][6])
            fs.save_mat(data["mat"])
            data["ready"] = False

            if not tm.ok():
                continue

            # convert width
            import copy
            str_data = copy.deepcopy(data["mat"])
            for i, row in enumerate(str_data):
                for j, col in enumerate(row):
                    str_data[i][j] = "{:.3f}".format(col)

            tdata = header + str_data
            # tdata = header + data["mat"]

            table = AsciiTable(tdata)
            if os.name == "nt":
                os.system("cls")
            else:
                os.system("clear")

            print("recv bytes: ", data["recv_bytes"], "scans: ",
                  data["scans"], "resets: ", data["resets"])
            print(table.table)


if __name__ == "__main__":
    # do_recv()
    # generate mock data
    do_recv_raw()
