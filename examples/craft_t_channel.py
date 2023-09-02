from adsc_transmitter import (
    modulate,
    get_t_channel_bits,
    down_basic_report,
    get_acars_message,
    down_earth_reference_group,
)
import numpy as np
import random

time = (5, 10)
data_bits = []

# data = [
#     {
#         "lat": 61.469,
#         "long": -57.455,
#         "alt": 34000,
#         "call": ".D-ABYM",
#         "id": "3c4b2d",
#         "ubi": "A",
#     },
#     {
#         "lat": 59.000,
#         "long": -50.009,
#         "alt": 36000,
#         "call": ".G-YMMA",
#         "id": "4007ec",
#         "ubi": "B",
#     },
#     {
#         "lat": 57.381,
#         "long": -52.511,
#         "alt": 36000,
#         "call": ".D-ABPE",
#         "id": "3c4A05",
#         "ubi": "C",
#     },
#     {
#         "lat": 55.940,
#         "long": -50.321,
#         "alt": 37000,
#         "call": ".D-AIKN",
#         "id": "3c656e",
#         "ubi": "D",
#     },
#     {
#         "lat": 56.014,
#         "long": -47.867,
#         "alt": 36000,
#         "call": ".PH-BQN",
#         "id": "4841ad",
#         "ubi": "E",
#     },
#     {
#         "lat": 55.442,
#         "long": -48.180,
#         "alt": 37700,
#         "call": ".D-AIKH",
#         "id": "3c6568",
#         "ubi": "F",
#     },
#     {
#         "lat": 56.296,
#         "long": -44.133,
#         "alt": 38000,
#         "call": ".EI-EJO",
#         "id": "4caa6d",
#         "ubi": "G",
#     },
#     {
#         "lat": 57.713,
#         "long": -42.005,
#         "alt": 34000,
#         "call": ".N2639U",
#         "id": "a28dc8",
#         "ubi": "H",
#     },
# ]

# data = [
#     {
#         "lat": 61.469,
#         "long": -51.455,
#         "alt": 34000,
#         "call": ".D-ABYM",
#         "id": "3c4b2d",
#         "ubi": "A",
#     },
#     {
#         "lat": 60.000,
#         "long": -50.009,
#         "alt": 36000,
#         "call": ".G-YMMA",
#         "id": "4007ec",
#         "ubi": "B",
#     },
#     {
#         "lat": 60.507,
#         "long": -50.511,
#         "alt": 36000,
#         "call": ".D-ABPE",
#         "id": "3c4A05",
#         "ubi": "C",
#     },
#     {
#         "lat": 59.913,
#         "long": -51.321,
#         "alt": 37000,
#         "call": ".D-AIKN",
#         "id": "3c656e",
#         "ubi": "D",
#     },
#     {
#         "lat": 60.255,
#         "long": -51.001,
#         "alt": 36000,
#         "call": ".PH-BQN",
#         "id": "4841ad",
#         "ubi": "E",
#     },
#     {
#         "lat": 61.218,
#         "long": -49.978,
#         "alt": 37700,
#         "call": ".D-AIKH",
#         "id": "3c6568",
#         "ubi": "F",
#     },
#     {
#         "lat": 60.832,
#         "long": -50.856,
#         "alt": 38000,
#         "call": ".EI-EJO",
#         "id": "4caa6d",
#         "ubi": "G",
#     },
#     {
#         "lat": 61.509,
#         "long": -50.736,
#         "alt": 34000,
#         "call": ".N2639U",
#         "id": "a28dc8",
#         "ubi": "H",
#     },
#      {
#         "lat": 60.0,
#         "long": -51.455,
#         "alt": 34000,
#         "call": ".D-ABYM",
#         "id": "3c4b2d",
#         "ubi": "A",
#     },
# ]

data = [
    {
        "lat": 61.469,
        "long": -51.455,
        "alt": 34000,
        "call": ".D-ABYM",
        "id": "3c4b2d",
        "ubi": "A",
    },
    {
        "lat": 60.0,
        "long": -51.455,
        "alt": 34000,
        "call": ".D-ABYM",
        "id": "3c4b2d",
        "ubi": "A",
    },
    {
        "lat": 59.0,
        "long": -51.455,
        "alt": 34000,
        "call": ".D-ABYM",
        "id": "3c4b2d",
        "ubi": "A",
    },
    {
        "lat": 58.0,
        "long": -51.455,
        "alt": 34000,
        "call": ".D-ABYM",
        "id": "3c4b2d",
        "ubi": "A",
    },
    {
        "lat": 57.0,
        "long": -50.455,
        "alt": 34000,
        "call": ".D-ABYM",
        "id": "3c4b2d",
        "ubi": "A",
    },
    {
        "lat": 57.0,
        "long": -48.455,
        "alt": 34000,
        "call": ".D-ABYM",
        "id": "3c4b2d",
        "ubi": "A",
    },
]

for i, d in enumerate(data):
    adsc_message = down_basic_report(
        d["lat"], d["long"], d["alt"], time, 1, 7, 1
    ) + down_earth_reference_group(248, 210, 1750)
    acars_message = get_acars_message(
        adsc_message,
        d["call"],
        d["id"],
        d["ubi"],
        message_source="F",
        message_number="11",
        bsc="A",
        airline_id="LH",
        flight_id="1234",
        up=False,
    )
    data_bits.append(get_t_channel_bits(acars_message, d["id"], "90", 7, i, 1))


bits_to_modulate = []

for bits in data_bits:
    for _ in range(5000):
        bits_to_modulate.append(random.randint(0, 1))
    bits_to_modulate += bits


with open("./fake_t_packet.BIN", "wb") as f:
    iq_samples = modulate(bits_to_modulate, data_rate=1200)
    f.write(iq_samples.tobytes())
