from adsc_transmitter import (
    get_t_channel_bits,
    get_acars_message,
    down_vertical_change_event,
    modulate_rrc
)
import random

time = (5, 10)

adsc_message = down_vertical_change_event(57.0, -48.455, 34000, time, 1, 7, 1, 20, 1000, 10)
acars_message = get_acars_message(adsc_message, ".D-ABYM", "BZVCAYA", "A", message_source="F", message_number="11", bsc="A", airline_id="LH", flight_id="1234", up=False)

data_bits = [get_t_channel_bits(acars_message, "06E010", "90", 7, 0, 1)]
bits_to_modulate = get_t_channel_bits(acars_message, "06E010", "90", 7, 0, 1)

with open("./fake_t_packet.BIN", "wb") as f:
    iq_samples = modulate_rrc(bits_to_modulate, data_rate=1200)
    f.write(iq_samples.tobytes())
