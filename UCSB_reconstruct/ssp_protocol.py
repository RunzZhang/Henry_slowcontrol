"""
Python port of SSP_Protocol_Int0v4.js — the serial framing the FDC1004EVM's
onboard MSP430 (USB-to-I2C bridge) uses. Ported directly from the GUI's own
protocol file rather than reverse-engineered from traffic captures.
"""

NAMESPACE = 0x4C  # ASCII 'L'

CMD_START_STREAM = 0x05
CMD_STOP_ALL_STREAMS = 0x07
CMD_SMBUS_READ = 0x12
CMD_SMBUS_WRITE = 0x13
CMD_READ_ALL_DATA = 0x30

ERR_OK = 0x00

FDC1004_I2C_ADDR = 0x50


def crc8(data):
    """Non-reflected CRC-8, poly 0x07, init 0x00 — matches npm 'crc' package's crc8()."""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


def _finish(packet):
    packet.append(crc8(bytes(packet)))
    return bytes(packet)


def build_write_i2c(address, register, data=b''):
    data = bytes(data)
    packet = [NAMESPACE, CMD_SMBUS_WRITE, 0x01, ERR_OK, 2 + len(data), address, register]
    packet.extend(data)
    return _finish(packet)


def build_read_i2c(address, register, read_bytes):
    packet = [NAMESPACE, CMD_SMBUS_READ, 0x01, ERR_OK, 3, address, register, read_bytes]
    return _finish(packet)


def build_start_stream(device_address=FDC1004_I2C_ADDR):
    packet = [
        NAMESPACE, CMD_START_STREAM, 0x01, ERR_OK, 6,
        0x01,        # process count
        0x00, 0x01,  # interval LSB, MSB (hardcoded by the GUI itself)
        0x04,        # format
        CMD_READ_ALL_DATA,
        device_address,
    ]
    return _finish(packet)


def build_stop_stream():
    packet = [NAMESPACE, CMD_STOP_ALL_STREAMS, 0x01, ERR_OK, 0]
    return _finish(packet)


def check_header(frame, expected_cmd):
    return (
        len(frame) >= 5
        and frame[0] == NAMESPACE
        and frame[1] == expected_cmd
        and frame[3] == ERR_OK
    )


def parse_read_i2c_response(frame):
    if not check_header(frame, CMD_SMBUS_READ) or len(frame) < 7:
        return None
    value_bytes = frame[4] - 2
    return frame[7:7 + value_bytes]


def _to_signed24(msb, mid, lsb):
    value = (msb << 16) | (mid << 8) | lsb
    if value & 0x800000:
        value -= 1 << 24
    return value


FDC1004_STREAM_FRAME_LEN = 19  # header(6) + 4ch * 3 bytes + CRC


def parse_fdc1004_stream_frame(frame):
    """
    Parse one READ_ALL_DATA stream frame from an FDC1004EVM. Validates the
    header, declared data length, AND the trailing CRC8 — this is what lets
    a caller detect a misaligned/desynced byte stream instead of silently
    reading garbage as if it were valid channel data.
    Returns a list of 4 signed 24-bit raw channel values, or None.
    """
    if len(frame) != FDC1004_STREAM_FRAME_LEN:
        return None
    if not check_header(frame, CMD_READ_ALL_DATA):
        return None
    if frame[4] != 13:
        return None
    if crc8(frame[:-1]) != frame[-1]:
        return None
    offset = 6
    channels = []
    for ch in range(4):
        b = frame[offset:offset + 3]
        channels.append(_to_signed24(b[0], b[1], b[2]))
        offset += 3
    return channels


def raw_to_pf(raw_value):
    """FDC1004 24-bit measurement result -> capacitance in pF (datasheet conversion)."""
    return raw_value / (1 << 19)
