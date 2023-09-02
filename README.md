## ADS-C Spoofer
This project includes code to create, encode and modulate ADS-C messages over ACARS using the Inmarsat satellite network. 

See [adsc.py](adsc_spoofer/src/adsc.py) for possible ADS-C messages. 

### Build project
```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

### Examples

Create P Channel (uplink) packets:
```
python3 examples/craft_p_channel.py
```

Create T Channel (downlink) packets:
```
python3 examples/craft_t_channel.py
```

Create R Channel (downlink) packets (work in progress):
```
python3 examples/craft_r_channel.py
```

### Tests
```
python3 -m unittest
```

