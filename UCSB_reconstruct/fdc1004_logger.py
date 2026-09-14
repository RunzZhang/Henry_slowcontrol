"""
FDC1004EVM automated logger — talks directly to the EVM's onboard MSP430
(USB-to-I2C bridge) over its virtual COM port, bypassing the Sensing
Solutions GUI entirely. Protocol framing ported from SSP_Protocol_Int0v4.js.
"""

import json
import os
import statistics
import time

import serial

import ssp_protocol as ssp

try:
    from Henry_watchdog_database import mydatabase, datetime_in_1e5micro, datetime_in_1e5micro_gmt
    SLOWCONTROL_DB_AVAILABLE = True
except ImportError:
    SLOWCONTROL_DB_AVAILABLE = False

PORT = '/dev/ttyACM0'
BAUD = 9600  # CDC-ACM ignores this in practice; pyserial requires a value
# Resolved next to this file rather than relative to the current working
# directory — otherwise loading fails silently depending on which folder
# whatever imports this module (e.g. Henry_background.py) was launched from.
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# Set to True to write each averaged row into the slowcontrol MySQL
# database via Henry_watchdog_database.mydatabase, using the same
# DataStorage(Instrument, Time, Value, GMT) table every other sensor uses.
# Requires Henry_watchdog_database.py in the same folder and
# SLOWCONTROL_LOCAL_TOKEN set in the environment (same as the rest of the
# slowcontrol system).
ENABLE_SLOWCONTROL_DB = False
# "Instrument" name written for each channel — match your P&ID naming
# convention rather than using these placeholders as-is.
SLOWCONTROL_INSTRUMENT_NAMES = {1: 'FDC1004_CH1', 2: 'FDC1004_CH2', 3: 'FDC1004_CH3', 4: 'FDC1004_CH4'}

# FDC1004 register map (datasheet)
MEAS1_CONFIG, MEAS2_CONFIG, MEAS3_CONFIG, MEAS4_CONFIG = 0x08, 0x09, 0x0A, 0x0B
FDC_CONFIG = 0x0C
OFFSET_CAL_CIN1, OFFSET_CAL_CIN2, OFFSET_CAL_CIN3, OFFSET_CAL_CIN4 = 0x0D, 0x0E, 0x0F, 0x10
GAIN_CAL_CIN1, GAIN_CAL_CIN2, GAIN_CAL_CIN3, GAIN_CAL_CIN4 = 0x11, 0x12, 0x13, 0x14

# Maps config.json "id" strings to register addresses. MEASx_MSB/LSB and
# MANUFACTURER_ID/DEVICE_ID (present in a raw GUI-exported dump) are
# read-only result/ID registers and are intentionally not writable here.
WRITABLE_REGISTERS = {
    'CONF_MEAS1': MEAS1_CONFIG,
    'CONF_MEAS2': MEAS2_CONFIG,
    'CONF_MEAS3': MEAS3_CONFIG,
    'CONF_MEAS4': MEAS4_CONFIG,
    'FDC_CONF': FDC_CONFIG,
    'OFFSET_CAL_CIN1': OFFSET_CAL_CIN1,
    'OFFSET_CAL_CIN2': OFFSET_CAL_CIN2,
    'OFFSET_CAL_CIN3': OFFSET_CAL_CIN3,
    'OFFSET_CAL_CIN4': OFFSET_CAL_CIN4,
    'GAIN_CAL_CIN1': GAIN_CAL_CIN1,
    'GAIN_CAL_CIN2': GAIN_CAL_CIN2,
    'GAIN_CAL_CIN3': GAIN_CAL_CIN3,
    'GAIN_CAL_CIN4': GAIN_CAL_CIN4,
}
MEASX_CONFIG_IDS = {1: 'CONF_MEAS1', 2: 'CONF_MEAS2', 3: 'CONF_MEAS3', 4: 'CONF_MEAS4'}

CAPDAC_STEP_PF = 3.125  # each CAPDAC code step = 3.125 pF (confirmed: 9*3.125=28.125, 31*3.125=96.875 in the GUI's own CAPDAC table)

# Samples to discard right after starting the stream. The first conversion(s)
# after a config write can read saturated/stale before the new CAPDAC and
# gain/offset settings are reflected in a completed conversion cycle.
WARMUP_SAMPLES = 20

# Each averaged value covers all samples received over this many seconds.
AVERAGING_INTERVAL_S = 5.0


def load_config(config_path=CONFIG_PATH):
    """Load a register dump in the same format as capacitor_config.json:
    a list containing one list of {idx, id, value} entries, value as a hex
    string. Returns {id: int_value}."""
    with open(config_path) as f:
        entries = json.load(f)[0]
    return {e['id']: int(e['value'], 16) for e in entries}


def capdac_offsets_from_config(config):
    """
    Per-channel CAPDAC offset in pF, extracted from each channel's
    CONF_MEASx word (bits[9:5]) and added back to the raw ADC reading. The
    FDC1004's MEASx_MSB/LSB result is CHA measured *relative to* the
    internal CAPDAC (when CHB=CAPDAC), so the CAPDAC's own contribution has
    to be added back to get the true absolute capacitance on CHA. Deriving
    this from the loaded config (rather than hardcoding it) means it stays
    correct if the CAPDAC codes in config.json ever change.
    """
    offsets = {}
    for ch, conf_id in MEASX_CONFIG_IDS.items():
        word = config.get(conf_id, 0)
        capdac_code = (word >> 5) & 0x1F
        offsets[ch] = capdac_code * CAPDAC_STEP_PF
    return offsets


def write_register(ser, register, value_16bit):
    data = bytes([(value_16bit >> 8) & 0xFF, value_16bit & 0xFF])
    ser.write(ssp.build_write_i2c(ssp.FDC1004_I2C_ADDR, register, data))
    ack_len = 6 + (2 + len(data))  # header(6) + (addr+reg+data) + CRC
    ser.read(ack_len)


def apply_config(ser, config):
    # Force a full chip reset first (FDC_CONFIG bit15 = RST, self-clearing)
    # so every session starts from a clean, known state instead of
    # potentially carrying over stale config/conversion state from a
    # previous run — this is what was producing the frozen/saturated data
    # on some starts.
    write_register(ser, FDC_CONFIG, 0x8000)
    time.sleep(0.05)  # let the reset complete before writing new config
    for reg_id, address in WRITABLE_REGISTERS.items():
        if reg_id in config:
            write_register(ser, address, config[reg_id])
            time.sleep(0.005)  # small gap between writes so the I2C bus isn't hammered


def start_stream(ser, config_path=CONFIG_PATH):
    """Loads config.json, applies it to the chip, and starts streaming.
    Returns the per-channel CAPDAC offsets (pF) derived from that config,
    for use with StreamReader."""
    config = load_config(config_path)
    ser.reset_input_buffer()  # drop anything left over from a previous session
    apply_config(ser, config)
    ser.reset_input_buffer()  # drop config-write ACK stragglers before streaming starts
    ser.write(ssp.build_start_stream())
    ser.read(64)  # discard ack frame
    return capdac_offsets_from_config(config)


def stop_stream(ser):
    ser.write(ssp.build_stop_stream())
    ser.read(64)


class StreamReader:
    """
    Reads FDC1004 stream frames with self-resync: rather than trusting that
    every fixed-size read lands on a frame boundary (the cause of the
    channel-swap bug — a stray leftover byte shifts every subsequent read),
    it buffers incoming bytes and only accepts a slice once it passes the
    header AND CRC8 check. A bad alignment gets shifted byte-by-byte until
    it locks on, instead of silently mislabeling channels.
    """

    def __init__(self, ser, capdac_offsets):
        self.ser = ser
        self.capdac_offsets = capdac_offsets
        self.buf = bytearray()

    def read_sample(self):
        frame_len = ssp.FDC1004_STREAM_FRAME_LEN
        if len(self.buf) < frame_len:
            available = self.ser.in_waiting
            if available == 0:
                return None
            self.buf.extend(self.ser.read(min(available, frame_len - len(self.buf))))
        while len(self.buf) >= frame_len:
            candidate = bytes(self.buf[:frame_len])
            channels = ssp.parse_fdc1004_stream_frame(candidate)
            if channels is not None:
                del self.buf[:frame_len]
                return [
                    ssp.raw_to_pf(raw) + self.capdac_offsets[ch]
                    for ch, raw in enumerate(channels, start=1)
                ]
            del self.buf[0]  # misaligned: drop one byte and retry
        return None


def log_forever(ser, capdac_offsets, averaging_interval_s=AVERAGING_INTERVAL_S):
    reader = StreamReader(ser, capdac_offsets)

    slowcontrol_db = None
    if ENABLE_SLOWCONTROL_DB:
        if not SLOWCONTROL_DB_AVAILABLE:
            raise RuntimeError(
                'ENABLE_SLOWCONTROL_DB is True but Henry_watchdog_database.py '
                'was not importable (needs to be in the same folder)'
            )
        slowcontrol_db = mydatabase()

    # Discard the first few samples after starting: the FDC1004 can report
    # saturated/stale readings for a conversion cycle or two right after a
    # config write, before settling on the new CAPDAC/gain values.
    discarded = 0
    while discarded < WARMUP_SAMPLES:
        if reader.read_sample() is not None:
            discarded += 1

    channel_samples = [[], [], [], []]
    interval_start = time.perf_counter()

    while True:
        sample = reader.read_sample()
        if sample is not None:
            for ch in range(4):
                channel_samples[ch].append(sample[ch])

        if time.perf_counter() - interval_start < averaging_interval_s:
            continue
        if not channel_samples[0]:
            interval_start = time.perf_counter()
            continue

        means = [statistics.mean(vals) for vals in channel_samples]
        print('FDC1004 averages (pF):', means)

        if slowcontrol_db is not None:
            dt = datetime_in_1e5micro()
            gmt_dt = datetime_in_1e5micro_gmt()
            for ch in range(4):
                name = SLOWCONTROL_INSTRUMENT_NAMES[ch + 1]
                slowcontrol_db.insert_data_into_stack(name, dt, means[ch], gmt_dt)
            # same commit cycle as Henry_background.py's write_data()
            slowcontrol_db.sort_stack()
            slowcontrol_db.convert_stack_into_queries()
            slowcontrol_db.drop_stack()
            slowcontrol_db.db.commit()

        channel_samples = [[], [], [], []]
        interval_start = time.perf_counter()


if __name__ == '__main__':
    ser = serial.Serial(PORT, BAUD, timeout=1)
    try:
        capdac_offsets = start_stream(ser)
        log_forever(ser, capdac_offsets)
    except KeyboardInterrupt:
        pass
    finally:
        stop_stream(ser)
        ser.close()
