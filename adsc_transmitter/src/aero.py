import math
import numpy as np
from .utils import get_crc, to_bits, to_bytes
from commpy.filters import rrcosfilter


def get_noise(length: int):
    return np.random.normal(0, 1, length)


def diff_encode(bits):
    diff_bits = [bits[0]]
    for i, bit in enumerate(bits[1:]):
        diff_bits.append(bit ^ diff_bits[i])
    return diff_bits


def modulate(bits, data_rate=600):
    sample_rate = 1536000
    symbols_per_bit = int(sample_rate / data_rate)
    T = symbols_per_bit

    diff_bits = [bits[0]]
    for i, bit in enumerate(bits[1:]):
        diff_bits.append(bit ^ diff_bits[i])

    oscilator = 0
    oscilate_bits = []
    for bit in diff_bits:
        oscilate_bits.append(bit ^ oscilator)
        oscilator = 1 if oscilator == 0 else 0
    data = [x if x else -1 for x in oscilate_bits]

    odd = [0] * T + [x for x in data[1::2] for _ in range(2 * T)]
    even = [x for x in data[0::2] for _ in range(2 * T)] + [0] * T
    bits = [x for x in data for _ in range(T)] + [0] * T
    t = np.linspace(0, (len(data) + 1) * T, (len(data) + 1) * T)

    cos = np.cos(-np.pi / 2 + np.pi * t / (2 * T))
    sin = np.sin(-np.pi / 2 + np.pi * t / (2 * T))
    i = np.multiply(even, cos)
    r = np.multiply(odd, sin)

    return np.array(
        [item for sublist in zip(i, r) for item in sublist], dtype=np.float32
    )

def modulate_rrc(bits, data_rate=600):
    sample_rate = 1536000
    symbols_per_bit = int(sample_rate / data_rate)
    T = symbols_per_bit

    diff_bits = [bits[0]]
    for i, bit in enumerate(bits[1:]):
        diff_bits.append(bit ^ diff_bits[i])

    oscilator = 0
    oscilate_bits = []
    for bit in diff_bits:
        oscilate_bits.append(bit ^ oscilator)
        oscilator = 1 if oscilator == 0 else 0
    # data = [x if x else -1 for x in oscilate_bits]
    data = oscilate_bits

    odd_bits = [0] * T
    for i, x in enumerate(data[1::2]):
        bit = x if i % 2 == 0 else -x
        odd_bits.append(bit)
        odd_bits += [0] * (2 * T - 1)

    even_bits = []
    for i, x in enumerate(data[0::2]):
        bit = x if i % 2 == 0 else -x
        even_bits.append(bit)
        even_bits += [0] * (2 * T - 1)
    even_bits += [0] * T

    t_filter, rrc_filter = rrcosfilter(101, 0.4, 8, 1)
    i = np.convolve(even_bits, rrc_filter)
    r = np.convolve(odd_bits, rrc_filter)
    
    return np.array(
        [item for sublist in zip(i, r) for item in sublist], dtype=np.float32
    )

def aero_crc(data):
    return get_crc(data)


def scramble(data):
    initial_state = [1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1]

    output = []
    for bit in data:
        new_bit = initial_state[0] ^ initial_state[-1]
        output.append(new_bit ^ bit)
        initial_state = [new_bit] + initial_state[:-1]

    return output


def encode(data, initial_state):
    output = []
    state = initial_state

    for bit in data:
        output.append(bit ^ state[1] ^ state[2] ^ state[4] ^ state[5])
        output.append(bit ^ state[0] ^ state[1] ^ state[2] ^ state[5])
        state = [bit] + state[:-1]

    return output, state


def interleave(data, num_cols=6):
    rows = []
    for i in range(64):
        row = []
        for j in range(num_cols):
            row.append(data[j * 64 + i])
        rows.append(row)

    output_rows = []
    for i in range(64):
        output_rows.append(rows[i * 19 % 64])

    output = []
    for row in output_rows:
        output += row

    return output


def delay(data):
    return data[-6:] + data[:-6]


UNIQUE_WORD = [
    1, 1, 1, 0, 0, 0, 0, 1,
    0, 1, 0, 1, 1, 0, 1, 0,
    1, 1, 1, 0, 1, 0, 0, 0,
    1, 0, 0, 1, 0, 0, 1, 1
]
FORMAT_ID = [0, 0, 0, 1]
BOUNDARY_MARKER = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
# PREAMBLE = [0] * 126 + [0, 1] * 74
PREAMBLE = [0, 1] * 100


def get_p_frame_headers(data):
    return UNIQUE_WORD + FORMAT_ID + BOUNDARY_MARKER + data


def get_r_frame_headers(data):
    return PREAMBLE + UNIQUE_WORD + data


def get_p_frame(data, initial_state=[0, 0, 0, 0, 0, 0]):
    scrambled_data = scramble(data)

    encoded_data, state = encode(scrambled_data, initial_state)

    computed_interleaved = []
    for i in range(0, 1152, 384):
        computed_interleaved += interleave(encoded_data[i: i + 384])

    return get_p_frame_headers(computed_interleaved), state


def get_t_frame(data, initial_state=[0, 0, 0, 0, 0, 0]):
    scrambled_data = scramble(data)

    encoded_data, state = encode(scrambled_data, initial_state)

    computed_interleaved = []
    for i in range(0, 1152, 384):
        computed_interleaved += interleave(
            encoded_data[i: i + 384], num_cols=5)

    return computed_interleaved, state


def get_r_frame(data, initial_state=[0, 0, 0, 0, 0, 0]):
    scrambled_data = scramble(data)

    # Add 8 flush bits
    scrambled_data += [0] * 8
    encoded_data, state = encode(scrambled_data, initial_state)

    computed_interleaved = interleave(encoded_data, 5)

    return get_r_frame_headers(computed_interleaved), state


hex_to_iso5_map = {
    "0": [0, 0, 1, 1, 0, 0, 0, 0],
    "1": [0, 0, 1, 1, 0, 0, 0, 1],
    "2": [0, 0, 1, 1, 0, 0, 1, 0],
    "3": [0, 0, 1, 1, 0, 0, 1, 1],
    "4": [0, 0, 1, 1, 0, 1, 0, 0],
    "5": [0, 0, 1, 1, 0, 1, 0, 1],
    "6": [0, 0, 1, 1, 0, 1, 1, 0],
    "7": [0, 0, 1, 1, 0, 1, 1, 1],
    "8": [0, 0, 1, 1, 1, 0, 0, 0],
    "9": [0, 0, 1, 1, 1, 0, 0, 1],
    "a": [0, 1, 0, 0, 0, 0, 0, 1],
    "b": [0, 1, 0, 0, 0, 0, 1, 0],
    "c": [0, 1, 0, 0, 0, 0, 1, 1],
    "d": [0, 1, 0, 0, 0, 1, 0, 0],
    "e": [0, 1, 0, 0, 0, 1, 0, 1],
    "f": [0, 1, 0, 0, 0, 1, 1, 0],
}


USER_DATA = 0x71


def get_user_data_isu(
    aes_id, ges_id, q_no: int, ref_no: int, octet_no, first_sequence_no, data
):
    packet = USER_DATA.to_bytes(1, "big")
    packet += aes_id
    packet += ges_id
    packet += to_bytes(to_bits([q_no])[:4][::-1] + to_bits([ref_no])[:4][::-1])
    packet += to_bytes([0, 0] + to_bits([first_sequence_no])[:6][::-1])
    packet += to_bytes(to_bits([octet_no])[:4][::-1] + [0, 0, 0, 0])
    packet += data
    packet += to_bytes(aero_crc(to_bits(packet))[::-1])[::-1]
    return packet


def get_user_data_ssu(seq_no, q_no, ref_no, data):
    packet = to_bytes([1, 1] + to_bits([seq_no], length=6)[:6][::-1])
    packet += to_bytes(
        to_bits([q_no], length=4)[:4][::-1] +
        to_bits([ref_no], length=4)[:4][::-1]
    )
    packet += data
    packet += to_bytes(aero_crc(to_bits(packet, length=16))[::-1])[::-1]
    return packet


def get_user_data_r_channel(seq_no, su_type, q_no, ref_no, aes_id, ges_id, data):
    packet = to_bytes(to_bits([seq_no])[:4][::-1] +
                      to_bits([su_type])[:4][::-1])
    packet += to_bytes(to_bits([q_no])[:4][::-1] +
                       [1] + to_bits([ref_no])[:3][::-1])
    packet += aes_id
    packet += ges_id
    packet += data
    packet += to_bytes(aero_crc(to_bits(packet))[::-1])[::-1]
    return packet


def get_p_data_packets(aes_id, ges_id, q_no, ref_no, data):
    first_sequence_no = math.ceil((len(data) - 2) / 8)
    octet_no = len(data) - 2 - (first_sequence_no - 1) * 8
    data += (8 - octet_no) * b"\x00"
    packets = get_user_data_isu(
        aes_id, ges_id, q_no, ref_no, octet_no, first_sequence_no, data[:2]
    )
    data_pointer = 2
    seq_no = first_sequence_no - 1
    while seq_no >= 0:
        packets += get_user_data_ssu(
            seq_no, q_no, ref_no, data[data_pointer: data_pointer + 8]
        )
        seq_no -= 1
        data_pointer += 8
    return packets


def get_r_data_packets(aes_id, ges_id, q_no, ref_no, data):
    first_sequence_no = math.ceil((len(data)) / 11)
    last_su_type = len(data) - 11 * (first_sequence_no - 1)
    data += (11 - last_su_type) * b"\x00"

    packets = []
    seq_no = first_sequence_no - 1
    data_pointer = 0
    while seq_no >= 0:
        packets.append(
            get_user_data_r_channel(
                seq_no,
                11 if seq_no > 0 else last_su_type,
                q_no,
                ref_no,
                aes_id,
                ges_id,
                data[data_pointer: data_pointer + 11],
            )
        )
        seq_no -= 1
        data_pointer += 11
    return packets


def get_p_channel_bits(
    acars_message: bytes, aes_id: str, ges_id: str, q_no: int, ref_no: int, repeat=10
) -> list[int]:
    p_channel_packets = to_bits(
        get_p_data_packets(
            bytes.fromhex(aes_id), bytes.fromhex(
                ges_id), q_no, ref_no, acars_message
        )
    )
    # Fill remaining spaces in frames with dummy ISU and pack it into frames
    dummy_su = to_bits([16, 127, 0, 0, 0, 0, 0, 0, 0, 0])
    dummy_su = dummy_su + aero_crc(dummy_su)

    num_frames = len(p_channel_packets) // 576  # 6 blocks * 12 bytes * 8 bits
    output = []
    state = [0, 0, 0, 0, 0, 0]
    for _ in range(repeat):
        for i in range(num_frames):
            frame, state = get_p_frame(
                p_channel_packets[i * 576: (i + 1) * 576], state
            )
            output += frame

        # Add last frame and pad with dummy SU
        frame, state = get_p_frame(
            p_channel_packets[num_frames * 576:]
            + dummy_su * (6 - (len(p_channel_packets) -
                          576 * num_frames) // 96),
            state,
        )
        output += frame

    return output


def get_t_channel_bits(
    acars_message: bytes, aes_id: str, ges_id: str, q_no: int, ref_no: int, repeat=10
) -> list[int]:
    t_channel_packets = to_bits(
        get_p_data_packets(
            bytes.fromhex(aes_id), bytes.fromhex(
                ges_id), q_no, ref_no, acars_message
        )
    )
    burst_id = to_bits(bytes.fromhex(aes_id) + bytes.fromhex(ges_id))
    burst_id_crc = aero_crc(burst_id)
    t_frame = burst_id + burst_id_crc + t_channel_packets
    scrambled_data = scramble(t_frame) + [0] * 16
    encoded_data, _ = encode(scrambled_data, [0, 0, 0, 0, 0, 0])

    # 1 interleaver block with 5 cols, then the rest with 3
    interleaved_data = []
    interleaved_data += interleave(encoded_data[: 5 * 64], num_cols=5)
    for i in range(5 * 64, len(encoded_data), 3 * 64):
        interleaved_data += interleave(encoded_data[i: i + 3 * 64], num_cols=3)

    output = PREAMBLE + UNIQUE_WORD + interleaved_data

    return output


def get_r_channel_bits(
    acars_message: bytes, aes_id: str, ges_id: str, q_no: int, ref_no: int, repeat=10
) -> list[int]:
    return []
