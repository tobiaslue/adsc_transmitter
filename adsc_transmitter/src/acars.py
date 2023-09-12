from .utils import bytes_to_iso5, get_crc, parity, to_bits, to_bytes


def get_aircraft_number(aircraft_number: str) -> bytes:
    """ARINC-618, 2.3.3"""
    return bytes([ord(x) for x in aircraft_number])


def get_adsc_header(aircraft_number: str) -> bytes:
    """ARINC-622: 4.3.1"""
    imi = "ADS"
    return bytes([ord(x) for x in imi]) + get_aircraft_number(aircraft_number)


def get_ats_crc(data: bytes) -> bytearray:
    """ARINC-622: 2.2.3, AB"""
    crc = get_crc(to_bits(data, "big"))
    return to_bytes(crc)


def get_dummy_bytes() -> bytes:
    """The end of ads-c messages is always '\r\n'. Couldn't find any documentation"""
    return bytes([ord("\r"), ord("\n")])


def get_atc_center(atc_center: str) -> bytes:
    """ARINC-622: 4.3.1"""
    return bytes([ord("/")] + [ord(x) for x in atc_center] + [ord(".")])


def wrap_text_markers(data: bytes) -> bytes:
    """ARINC-618: 2.3.7, 2.3.9"""
    return bytes(b"\x02") + data + bytes(b"\x03")


def wrap_del_bytes(data: bytes) -> bytes:
    return bytes(b"\xff") * 2 + data + bytes(b"\x7f")


def get_ubi(ubi: str) -> bytes:
    """ARINC-618: 2.3.6"""
    return bytes([ord(ubi)])


def get_label(up: bool):
    """ARINC-622: 4.3.1, ARINC-618: 2.3.5, ARINC-620: 4.5"""
    if up:
        return bytes([ord("A"), ord("6")])
    return bytes([ord("B"), ord("6")])


def get_tak() -> bytes:
    """ARINC-618: 2.3.4"""
    return bytes([ord("\x15")])


def get_mode() -> bytes:
    """ARINC-618: 2.3.2"""
    return bytes([ord("2")])


def get_soh() -> bytes:
    """ARINC-618: 2.3.1"""
    return bytes([ord("\x01")])


def get_acars_headers(aircraft_number: str, ubi: str, up: bool) -> bytes:
    return (
        get_mode()
        + get_aircraft_number(aircraft_number)
        + get_tak()
        + get_label(up)
        + get_ubi(ubi)
    )


def get_acars_message(
    adsc_message: bytes,
    aircraft_number: str,
    atc_center: str,
    ubi: str,
    message_source="",
    message_number="",
    bsc="",
    airline_id="",
    flight_id="",
    up=True,
):
    adsc_header = get_adsc_header(aircraft_number)
    ats_crc = get_ats_crc(adsc_header + adsc_message)
    ats_message = (
        get_atc_center(atc_center)
        + adsc_header
        + bytes_to_iso5(adsc_message)
        + bytes_to_iso5(ats_crc)
    ) + get_dummy_bytes()
    if up:
        acars_message = get_acars_headers(aircraft_number, ubi, up) + wrap_text_markers(
            ats_message
        )
    else:
        acars_down_header = (
            message_source + message_number + bsc + airline_id + flight_id
        )
        acars_message = get_acars_headers(aircraft_number, ubi, up) + wrap_text_markers(
            acars_down_header.encode() + ats_message
        )
    with_parity = bytes([x + 128 if not parity(x) else x for x in acars_message])

    return wrap_del_bytes(
        get_soh() + with_parity + get_block_check_sequence(with_parity)
    )


def get_acars_crc(data) -> list[int]:
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1

    return to_bits(int.to_bytes(crc, 2, "little"), "big")


def get_block_check_sequence(data: bytes) -> bytes:
    """ARINC-618, 2.3.10"""
    crc = get_acars_crc(data)
    return to_bytes(crc)
