from enum import IntEnum
from time import time

import serial

from struct import pack, unpack


class PacketType(IntEnum):
    Unknown = 0
    MeasureData = 0x01


class Packet:
    SOF = 0xAA
    EOF = 0xCC

    HEADER_LEN = 4
    TAIL_LEN = 4

    def __init__(self):
        self.packet_type = PacketType.Unknown
        self.seq = 0
        self.payload = b''

    def load(self, buf):
        self.packet_type = PacketType(buf[1])
        payload_len = unpack('>H', buf[2:4])[0]

        self.payload = buf[4: 4 + payload_len]

        ei = Packet.HEADER_LEN + payload_len

        self.seq = unpack('B', buf[ei: ei + 1])[0]
        self.crc = buf[ei + 1: ei + 3]

    def _cal_crc(self, front_buf):
        # todo, crc
        return b'\x00\x00'

    def dump(self):
        b = pack('B', Packet.SOF)
        b += pack('B', self.packet_type.value)
        b += pack('>H', len(self.payload))
        b += self.payload
        b += pack('B', self.seq)
        b += self._cal_crc(b)
        b += pack('B', Packet.EOF)
        return b


class PacketSearchState(IntEnum):
    ExpectHeader = 1
    ExpectEnd = 2


class Communicator:
    def __init__(self, device, baudrate):
        self.ser = serial.Serial(device, baudrate, timeout=0.1)
        self._recv_buf = b''
        self._expect_len = Packet.HEADER_LEN
        self._search_state = PacketSearchState.ExpectHeader
        self._search_idx = 0
        self._recv_packets = []

        self.bytes_received = 0
        self.packet_received = 0

    def get_stats(self):
        return "Received Bytes {}, Valid packets {}".format(self.bytes_received, self.packet_received)

    def _search_packets(self):
        while (len(self._recv_buf) - self._search_idx) >= self._expect_len:
            if self._search_state == PacketSearchState.ExpectHeader:
                if self._recv_buf[self._search_idx] == Packet.SOF:
                    len_payload = 512
                    self._search_state = PacketSearchState.ExpectEnd
                    self._expect_len = len_payload + Packet.HEADER_LEN + Packet.TAIL_LEN
                else:
                    self._search_idx += 1
            elif self._search_state == PacketSearchState.ExpectEnd:
                if self._recv_buf[self._search_idx + self._expect_len - 1] == Packet.EOF:
                    p = Packet()
                    p.load(
                        self._recv_buf[self._search_idx: self._search_idx + self._expect_len])
                    self._recv_packets.append(p)
                    self.packet_received += 1
                    self._search_idx += self._expect_len
                    # (TODO. validfy packet)
                else:
                    self._search_state = PacketSearchState.ExpectHeader
                    self._expect_len = Packet.HEADER_LEN
                    self._search_idx += 1

        if self._search_idx != 0:
            self._recv_buf = self._recv_buf[self._search_idx:]
            self._search_idx = 0

    def recv(self):
        if len(self._recv_packets) > 0:
            return self._recv_packets.pop(0)

        while len(self._recv_packets) == 0:
            buf = self.ser.read(100)
            self.bytes_received += len(buf)
            self._recv_buf += buf
            self._search_packets()

        return self._recv_packets.pop(0)

    def send(self, packet):
        self.ser.write(packet.dump())
