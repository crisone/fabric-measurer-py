from serial import Serial
import time
import struct

SERIAL_PORT = '/dev/ttyS0'
BAUDRATE = 115200

mat = [[0 for i in range(16)]for i in range(16)]


def send():
    r = 0
    scans = 0
    s = Serial(SERIAL_PORT, BAUDRATE)
    while True:
        bytes = b''
        for i in range(16):
            v = r * 4096 + mat[r][i]
            bytes += struct.pack(">H", v)
        r += 1
        print(bytes)
        s.write(bytes)
        if r == 16:
            r = 0
            scans += 1
            if scans >= 256:
                scans = 0
            mat[scans//16][scans % 16] += 1
            time.sleep(0.1)


if __name__ == "__main__":
    send()
