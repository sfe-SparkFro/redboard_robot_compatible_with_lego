# Most useful link ever!
# https://github.com/pybricks/technical-info/blob/master/uart-protocol.md

from .lump_mode import LumpMode
from machine import UART, Timer
import struct
import time

# bits 7-6
MESSAGE_SYS = 0x00 # System message   0b00 << 6
MESSAGE_CMD = 0x40 # Command message  0b01 << 6
MESSAGE_INFO = 0x80 # Info message     0b10 << 6
MESSAGE_DATA = 0xC0 # Data message     0b11 << 6

# MESSAGE_SYS bits 2-0
BYTE_SYNC = 0x00 # Synchronization byte
BYTE_NACK = 0x02 # Not acknowledge byte (keep alive)
BYTE_ACK = 0x04 # Acknowledge byte

# MESSAGE_CMD bits 2-0
CMD_TYPE = 0x00 # CMD command - TYPE     (device type for VM reference)
CMD_MODES = 0x01 # CMD command - MODES    (number of supported modes minus one)
CMD_SPEED = 0x02 # CMD command - SPEED    (maximum communication speed)
CMD_SELECT = 0x03 # CMD command - SELECT   (select mode)
CMD_WRITE = 0x04 # CMD command - WRITE    (write to device)
CMD_EXT_MODE = 0x06 # CMD command - EXT_MODE (value will be added to mode in CMD_WRITE_DATA - LPF2 only)
CMD_VERSION = 0x07 # CMD command - VERSION  (device firmware and hardware versions)

# SECOND INFO BYTE
INFO_NAME = 0x00 # INFO command - NAME    (device name)
INFO_RAW = 0x01 # INFO command - RAW     (device RAW value span)
INFO_PCT = 0x02 # INFO command - PCT     (device PCT value span)
INFO_SI = 0x03 # INFO command - SI      (device SI  value span)
INFO_UNITS = 0x04 # INFO command - UNITS   (device SI  unit symbol)
INFO_MAPPING = 0x05 # INFO command - MAPPING (input/output value type flags)
INFO_MODE_COMBOS = 0x06 # INFO command - COMBOS  (mode combinations - LPF2-only)
INFO_UNK7 = 0x07 # INFO command - unknown (LPF2-only)
INFO_UNK8 = 0x08 # INFO command - unknown (LPF2-only)
INFO_UNK9 = 0x09 # INFO command - unknown (LPF2-only)
INFO_UNK10 = 0x0a # INFO command - unknown (LPF2-only)
INFO_UNK11 = 0x0b # INFO command - unknown (LPF2-only)
INFO_UNK12 = 0x0c # INFO command - unknown (LPF2-only)
INFO_MODE_PLUS_8 = 0x20 # Bit flag used in powered up devices to indicate that the mode is 8 + the mode specified in the first byte
INFO_FORMAT = 0x80 # INFO command - FORMAT  (device data sets and format)

buf_size = 1024
max_msg_size = 32+1+1+1 # max data size + header + checksum + extra header byte for info messages

class LumpDevice():
    def __init__(self, tx, rx, freq=10):
        self.tx = tx
        self.rx = rx
        self.u = UART(0, tx=self.tx, rx=self.rx, baudrate=2400, rxbuf=buf_size)
        self.buf = bytearray(max_msg_size)
        self.timer = Timer(mode=Timer.PERIODIC, freq=freq, callback=lambda t: self.process())
        self.msg_started = False
        self.synced = False
        self.value = 0
        self.ack = False
        self.ad_started = False
        self.mode = 0
        self.modes = []

    def begin(self):
        while self.ack == False:
            pass

    # Processes any messages in the buffer
    def process(self):
        # Send heartbeat
        if self.synced == True:
            self.send_nack()

        # Loop until we have processed as much as we can
        while True:
            # If no more bytes are left, nothing to do
            if self.u.any() == 0:
                return
            
            # If we're waiting for a message to start, get the header byte
            if self.msg_started == False:
                self.u.readinto(self.buf, 1)
                self.msg_started = True
            
            # Parse the header byte
            msg_typ = self.buf[0] & 0xC0
            msg_len = 1<<((self.buf[0] & 0x38) >> 3)
            msg_cmd = self.buf[0] & 0x07

            # System messages are just a single byte with no data or checksum
            if msg_typ == MESSAGE_SYS:
                self.msg_started = False
                # print("S:", end=" ")
                if msg_cmd == BYTE_SYNC:
                    # print("Sync")
                    pass
                elif msg_cmd == BYTE_NACK:
                    # print("Nack")
                    pass
                elif msg_cmd == BYTE_ACK:
                    if self.ad_started == True:
                        self.start_sync()
                        # time.sleep(0.01)
                        # lump.send_cmd_select(3)
                        # time.sleep(0.01)
                        # lump.send_cmd(CMD_WRITE, bytes([0, 0, 0, 0]))
                        # time.sleep(0.01)
                        # lump.send_cmd_select(6)
                        self.ack = True
                    # print("Ack")
                else:
                    # print("Unknown system message")
                    pass

                # Move to the next message
                continue

            # Compute number of bytes remaining in the message
            remaining_len = msg_len + 1 # +1 for checksum
            if (msg_typ & 0xC0) == MESSAGE_INFO:
                # +1 for extra header byte for info messages
                remaining_len += 1

            # Check if we have the rest of the message
            if self.u.any() >= remaining_len:
                # Read the rest of the message into the buffer
                # https://github.com/micropython/micropython/issues/19133
                # self.u.readinto(self.buf[1:], remaining_len)
                self.buf[1:1+remaining_len] = self.u.read(remaining_len)
                self.msg_started = False
            else:
                # Not enough bytes yet, wait for the next interrupt
                return

            # Compute the checksum
            checksum = 0xFF
            for i in range(remaining_len):
                checksum ^= self.buf[i]
            
            # Check the checksum
            if checksum != self.buf[remaining_len]:
                # print("Invalid checksum")
                # We might be out of sync, read out everything to flush it
                _ = self.u.read()
                self.msg_started = False
                return
            
            # Extract the data
            data = self.buf[1:remaining_len]
            # Skip second header byte for info messages
            if msg_typ == MESSAGE_INFO:
                data = data[1:]
            
            if msg_typ == MESSAGE_CMD:
                # print("C:", end=" ")
                if msg_cmd == CMD_TYPE:
                    # print("Device type number:", data[0])
                    self.ad_started = True
                    print("Sync started")
                elif msg_cmd == CMD_MODES and self.ad_started:
                    modes1 = data[0] + 1
                    views1 = 0 if msg_len < 2 else data[1] + 1
                    modes2 = 0 if msg_len < 3 else data[2] + 1
                    views2 = 0 if msg_len < 4 else data[3] + 1
                    self.modes = [LumpMode() for _ in range(modes1 + modes2)]
                    # print("Supported modes:", modes1, "views:", views1, "LPF2 modes:", modes2, "LPF2 views:", views2)
                elif msg_cmd == CMD_SPEED and self.ad_started:
                    speed = data[3] << 24 | data[2] << 16 | data[1] << 8 | data[0]
                    # print("Max speed:", speed)
                elif msg_cmd == CMD_SELECT and self.ad_started:
                    # print("Selected mode:", data[0])
                    pass
                elif msg_cmd == CMD_WRITE and self.ad_started:
                    # print("Write to device:", data)
                    pass
                elif msg_cmd == CMD_EXT_MODE and self.ad_started:
                    # print("Extended mode:", data)
                    pass
                elif msg_cmd == CMD_VERSION and self.ad_started:
                    fw_major = data[3] >> 4
                    fw_minor = data[3] & 0x0F
                    fw_revision = data[2]
                    fw_build = ((data[1] & 0x0F) << 8) | data[0]
                    hw_major = data[7] >> 4
                    hw_minor = data[7] & 0x0F
                    hw_revision = data[6]
                    hw_build = ((data[5] & 0x0F) << 8) | data[4]
                    # print("FW v{}.{}.{:02}.{:03}, HW v{}.{}.{:02}.{:03}".format(fw_major, fw_minor, fw_revision, fw_build, hw_major, hw_minor, hw_revision, hw_build))
                else:
                    # print("Unknown command message")
                    pass
            elif msg_typ == MESSAGE_INFO and self.ad_started:
                # print("I:", end=" ")
                # Message command is actually the mode number
                mode = msg_cmd
                # Second byte is the info type
                info_typ = self.buf[1]

                # If the INFO_MODE_PLUS_8 bit is set, add 8 to the mode number
                if info_typ & INFO_MODE_PLUS_8:
                    mode += 8

                if info_typ == INFO_NAME:
                    name = data.split(b'\x00')[0].decode('ascii')
                    self.modes[mode].name = name
                    # print("Mode {}: {}".format(mode, name))
                    # 6 flag bytes may follow the name
                    # name_len = len(name) + 1
                    # if len(data) > name_len + 6:
                    #     flags = data[name_len:name_len + 6]
                    #     print("  Flags:", flags)
                elif info_typ == INFO_RAW:
                    min_val = self.int32_to_float(data[0:4])
                    max_val = self.int32_to_float(data[4:8])
                    self.modes[mode].raw_min = min_val
                    self.modes[mode].raw_max = max_val
                    # print("  RAW value range: {} to {}".format(min_val, max_val))
                elif info_typ == INFO_PCT:
                    min_val = self.int32_to_float(data[0:4])
                    max_val = self.int32_to_float(data[4:8])
                    self.modes[mode].pct_min = min_val
                    self.modes[mode].pct_max = max_val
                    # print("  PCT value range: {} to {}".format(min_val, max_val))
                elif info_typ == INFO_SI:
                    min_val = self.int32_to_float(data[0:4])
                    max_val = self.int32_to_float(data[4:8])
                    self.modes[mode].si_min = min_val
                    self.modes[mode].si_max = max_val
                    # print("  SI value range: {} to {}".format(min_val, max_val))
                elif info_typ == INFO_UNITS:
                    units = data.split(b'\x00')[0].decode('ascii')
                    self.modes[mode].units = units
                    # print("  SI units:", units)
                elif info_typ == INFO_MAPPING:
                    # print("  Mapping flags: input: 0x{:X} output: 0x{:X}".format(data[0], data[1]))
                    pass
                elif info_typ == INFO_FORMAT:
                    data_sets = data[0]
                    format = data[1]
                    figures = data[2]
                    decimals = data[3]
                    self.modes[mode].format = (data_sets, format, figures, decimals)
                    self.modes[mode].data = [0] * data_sets
                    # print("  Data sets: {} format: {} figures: {} decimals: {}".format(data_sets, format, figures, decimals))
                elif info_typ == INFO_MODE_COMBOS:
                    # print("Mode combinations:", end=" ")
                    for i in range(0, len(data), 2):
                        combo = (data[i] << 8) | data[i+1]
                        # print("0x{:04X}".format(combo), end=" ")
                    # print()
                else:
                    # print("Unknown info type:", info_typ)
                    pass
            elif msg_typ == MESSAGE_DATA and self.ad_started:
                if self.modes[self.mode].format[LumpMode.FORMAT_FORMAT] == LumpMode.FORMAT_INT8:
                    for i in range(self.modes[self.mode].format[LumpMode.FORMAT_DATA_SETS]):
                        value = data[i]
                        if value & 0x80:
                            value -= 0x100
                        self.modes[self.mode].data[i] = value
                elif self.modes[self.mode].format[LumpMode.FORMAT_FORMAT] == LumpMode.FORMAT_INT16:
                    for i in range(self.modes[self.mode].format[LumpMode.FORMAT_DATA_SETS]):
                        value = (data[2*i+1] << 8) | data[2*i]
                        if value & 0x8000:
                            value -= 0x10000
                        self.modes[self.mode].data[i] = value
                elif self.modes[self.mode].format[LumpMode.FORMAT_FORMAT] == LumpMode.FORMAT_INT32:
                    for i in range(self.modes[self.mode].format[LumpMode.FORMAT_DATA_SETS]):
                        value = (data[4*i+3] << 24) | (data[4*i+2] << 16) | (data[4*i+1] << 8) | data[4*i]
                        if value & 0x80000000:
                            value -= 0x100000000
                        self.modes[self.mode].data[i] = value
                elif self.modes[self.mode].format[LumpMode.FORMAT_FORMAT] == LumpMode.FORMAT_FLOAT:
                    for i in range(self.modes[self.mode].format[LumpMode.FORMAT_DATA_SETS]):
                        value = self.int32_to_float(data[4*i:4*i+4])
                        self.modes[self.mode].data[i] = value
                # # print("D:", end=" ")
                # if len(data) == 2:
                #     value = data[1] << 8 | data[0]
                #     if value & 0x8000:
                #         value -= 0x10000
                #     # print("Value:", value)
                #     self.value = value
                # elif len(data) == 8:
                #     # for i in range(8):
                #     #     print("{:02X}".format(data[i]), end="")
                #     # print()
                #     self.h = data[1] << 8 | data[0]
                #     self.s = data[3] << 8 | data[2]
                #     self.v = data[5] << 8 | data[4]
                #     # i = data[7] << 8 | data[6]
                #     # print("R: {:04} G: {:04} B: {:04} I: {:04}".format(r, g, b, i))
                else:
                    # print("Data message:", data)
                    pass

            # Move to the next message
            continue
    
    def int32_to_float(self, values):
        value = values[3] << 24 | values[2] << 16 | values[1] << 8 | values[0]
        # Convert a 32-bit integer to a float using IEEE 754 format
        return struct.unpack('f', struct.pack('I', value))[0]

    def send_sync(self):
        self.u.write(bytes([MESSAGE_SYS | BYTE_SYNC]))

    def send_nack(self):
        self.u.write(bytes([MESSAGE_SYS | BYTE_NACK]))

    def send_ack(self):
        self.u.write(bytes([MESSAGE_SYS | BYTE_ACK]))

    def bit_length(self, n):
        return len(bin(abs(n))) - 2 if n != 0 else 0

    def send_cmd(self, cmd, data):
        msg_len = len(data)
        header = MESSAGE_CMD | ((self.bit_length(msg_len) - 1) << 3) | cmd
        checksum = 0xff
        checksum ^= header
        for b in data:
            checksum ^= b
        self.u.write(bytes([header]) + data + bytes([checksum]))

    def send_cmd_speed(self, speed):
        data = bytes([
            speed & 0xFF,
            (speed >> 8) & 0xFF,
            (speed >> 16) & 0xFF,
            (speed >> 24) & 0xFF
        ])
        self.send_cmd(CMD_SPEED, data)

    def start_sync(self):
        # self.send_cmd_speed(115200)
        # self.ack = False
        # while not self.ack:
        #     pass
        self.send_ack()
        time.sleep(0.01)
        print("Synchronized at 115200 baud")
        self.u = UART(0, tx=self.tx, rx=self.rx, baudrate=115200, rxbuf=buf_size)
        self.send_nack()
        self.synced = True
        # self.timer = Timer(mode=Timer.PERIODIC, freq=2, callback=lambda t: self.foo())

    def reset_uart(self):
        self.u = UART(0, tx=self.tx, rx=self.rx, baudrate=2400, rxbuf=buf_size)
        self.timer.deinit()

    def send_cmd_select(self, mode):
        self.send_cmd(CMD_SELECT, bytes([mode]))

    def get_mode_index_by_name(self, name):
        for i, mode in enumerate(self.modes):
            if mode.name == name:
                return i
        return -1

    def set_mode(self, mode):
        self.mode = mode
        if self.synced:
            self.send_cmd_select(mode)
