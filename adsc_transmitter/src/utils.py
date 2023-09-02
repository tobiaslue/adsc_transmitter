
def get_crc(data) -> list[int]:
    crc = 0xFFFF
    for bit in data:
        crc_bit = crc & 1
        crc >>= 1
        if (crc_bit ^ bit):
            crc = crc ^ 0x8408

    output = [1 if digit == "1" else 0 for digit in bin(crc ^ 0xFFFF)[2:]]
    return output[::-1] + [0] * (16 - len(output))


def to_bits(data, endianess="little", length=0):
    output = []

    if endianess == "little":
        for number in data:
            bits = [1 if x == "1" else 0 for x in bin(number)[2:][::-1]]
            output += bits + [0] * (8 - len(bits))
    else:
        for number in data:
            bits = [1 if x == "1" else 0 for x in bin(number)[2:]]
            output += [0] * (8 - len(bits)) + bits

    if length and len(output) > length:
        output = output[-length:] if endianess == "big" else output[:length]
    elif length and len(output) < length:
        output = [0] * (length - len(output)) + \
            output if endianess == "big" else output + \
            [0] * (length - len(output))

    return output

# https://stackoverflow.com/questions/32675679/convert-binary-string-to-byte-in-python-3


def to_bytes(data:  list[int]) -> bytearray:
    v = int("".join([str(x) for x in data]), 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytearray(b[::-1])


def parity(x):
    parity = False
    while x:
        parity = not parity
        x = x & (x - 1)

    return int(parity)


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


def bytes_to_iso5(data):
    hex_data = "".join(["0x{:02x}".format(x)[2:] for x in data])
    output = []
    for char in hex_data:
        output += hex_to_iso5_map[char]
    return to_bytes(output)


def ascii_to_iso_5(data):
    output = []
    for char in data:
        if char.isdigit():
            output += hex_to_iso5_map[char][2:]
        else:
            output += [int(bit) for bit in bin(ord(char))[3:]]
    return output
