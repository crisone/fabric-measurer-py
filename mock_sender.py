import time
from struct import pack

from protocol import Packet, PacketType
from protocol import Communicator

SERIAL_PORT = '/dev/ttyS0'
BAUDRATE = 115200


def send_forever():
    c = Communicator(SERIAL_PORT, BAUDRATE)

    seq = 0

    data = [0] * 256

    while True:
        p = Packet()
        p.seq = seq
        p.packet_type = PacketType.MeasureData
        data[seq] += 1
        p.payload = pack('>256H', *data)
        c.send(p)
        time.sleep(0.1)

        seq += 1
        if seq > 255:
            seq = 0


if __name__ == "__main__":
    send_forever()
