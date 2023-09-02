"""See ARINC-745 attachment 8-2"""

from .utils import to_bytes, to_bits, ascii_to_iso_5


def up_cancel_all_contracts() -> bytes:
    return bytes([1])


def up_cancel_contract(contract_number: int) -> bytes:
    return bytes([2, contract_number])


def up_cancel_emergency_mode(contract_number: int) -> bytes:
    return bytes([6, contract_number])


def up_periodic_contract(
    contract_number: int, emergency_contract=False, **kwargs
) -> bytes:
    reporting_intervalal_tag = kwargs.get("reporting_intervalal_tag", None)
    flight_id_group = kwargs.get("flight_id_group", None)
    predicted_route_group = kwargs.get("predicted_route_group", None)
    earth_reference_group = kwargs.get("earth_reference_group", None)
    meteorological_group_modulus = kwargs.get("meteorological_group_modulus", None)
    airframe_id_group = kwargs.get("airframe_id_group", None)
    air_reference_group = kwargs.get("air_reference_group", None)
    aircraft_intent_group = kwargs.get("aircraft_intent_group", None)

    output = bytes([9 if emergency_contract else 7, contract_number])

    if reporting_intervalal_tag is not None:
        output += bytes([11])
        output += to_bytes(
            to_bits([reporting_intervalal_tag["sf"]], "big", 2)
            + to_bits([reporting_intervalal_tag["rate"]], "big", 6)
        )

    if flight_id_group is not None:
        output += bytes([12])
        output += bytes([flight_id_group])

    if predicted_route_group is not None:
        output += bytes([13])
        output += bytes([predicted_route_group])

    if earth_reference_group is not None:
        output += bytes([14])
        output += bytes([earth_reference_group])

    if meteorological_group_modulus is not None:
        output += bytes([16])
        output += bytes([meteorological_group_modulus])

    if airframe_id_group is not None:
        output += bytes([17])
        output += bytes([airframe_id_group])

    if air_reference_group is not None:
        output += bytes([15])
        output += bytes([air_reference_group])

    if aircraft_intent_group is not None:
        output += bytes([21])
        output += bytes(
            [aircraft_intent_group.group_modulus, aircraft_intent_group.projection_time]
        )
    return output


def up_event_contract(contract_number: int, **kwargs) -> bytes:
    vertical_rate_change = kwargs.get("vertical_range_change", None)
    altitude_range = kwargs.get("altitude_range", None)
    waypoint_change = kwargs.get("waypoint_change", None)
    lateral_deviation = kwargs.get("lateral_deviation", None)

    output = bytes([8, contract_number])

    if vertical_rate_change is not None:
        output += bytes([18])
        output += bytes([vertical_rate_change])

    if waypoint_change is not None:
        output += bytes([20])

    if altitude_range is not None:
        output += bytes([19])
        output += int.to_bytes(altitude_range["ceiling"], 2, "big")
        output += int.to_bytes(altitude_range["floor"], 2, "big")

    if lateral_deviation is not None:
        output += bytes([10])
        output += bytes([lateral_deviation])

    return output


def __get_figure_of_merit(redundancy, accuracy, tcas) -> list[int]:
    return [0, 0] + [tcas] + to_bits([accuracy], "big", 3) + [redundancy]


def down_acknowledgement(contract_number: int) -> bytes:
    return bytes([3, contract_number])


def down_negative_acknowledgement(
    contract_number: int, reason: int, extended_data=0
) -> bytes:
    output = bytes([4, contract_number, reason])
    if reason in [1, 2, 7]:
        output += bytes([extended_data])
    return output


def down_noncompliance(request_number: int, message_groups: list) -> bytes:
    encoded_data = []
    for group in message_groups:
        encoded_data += to_bits([group["group_tag"]], "big", 8)
        unavailable_parameters = group.get("unavailable_params", [])

        encoded_data += __get_noncompliance_params(
            group["group_undefined"], unavailable_parameters
        )
        for parameter in unavailable_parameters:
            encoded_data += to_bits([parameter], "big", 4)
        encoded_data += [0] * (
            0 if len(encoded_data) % 8 == 0 else 8 - len(encoded_data) % 8
        )

    return to_bytes(
        to_bits([5], "big", 8)
        + to_bits([request_number], "big", 8)
        + to_bits([len(message_groups)], "big", 8)
        + encoded_data
    )


def __get_noncompliance_params(
    group_undefined: bool, unavailable_params: list[int]
) -> list[int]:
    if group_undefined:
        return [1] + [0] * 7

    if len(unavailable_params) == 0:
        return [0] + [1] + [0] * 6

    return [0] * 4 + to_bits([len(unavailable_params)], "big", 4)


def down_cancel_emergency_mode() -> bytes:
    return bytes([6])


def down_meterological_group(
    wind_speed: int, direction: int, temperature: int
) -> bytes:
    wind_speed_number = int(wind_speed / 0.5)
    direction_number = int(direction / (180 / 2**8))
    temperature_number = int(temperature / 0.25)

    if temperature_number < 0:
        temperature_number = temperature_number + (1 << 12)

    return to_bytes(
        to_bits([16], "big", 8)
        + to_bits([wind_speed_number], "big", 9)
        + [0]
        + to_bits([direction_number], "big", 9)
        + to_bits([temperature_number], "big", 12)
        + [0]
    )


def down_air_reference_group(
    true_heading: int, mach_speed: float, vertical_rate: int
) -> bytes:
    true_heading_number = int(true_heading / (180 / 2**11))
    mach_speed_number = int(mach_speed / 0.0005)
    vertical_rate_number = int(vertical_rate / 16)

    return to_bytes(
        to_bits([15], "big", 8)
        + __get_reference_group(
            true_heading_number, mach_speed_number, vertical_rate_number
        )
    )


def down_flight_identification_group(flight_id: str) -> bytes:
    return to_bytes(
        to_bits([12], "big", 8)
        + ascii_to_iso_5(flight_id)
        + [1, 0, 0, 0, 0, 0] * (8 - len(flight_id))
    )


def __get_reference_group(heading: int, speed: int, vertical_rate: int) -> list[int]:
    heading_bits = [0] + to_bits([heading], "big", 12)
    speed_bits = to_bits([speed], "big", 13)

    if vertical_rate < 0:
        vertical_rate = vertical_rate + (1 << 12)
    vertical_rate_bits = to_bits([vertical_rate], "big", 12)

    return heading_bits + speed_bits + vertical_rate_bits + [0, 0]


def __get_coordinate(coordinate: float) -> list[int]:
    coordinate_number = int(coordinate / (180 / 2**20))
    if coordinate_number < 0:
        coordinate_number = coordinate_number + (1 << 21)
    return to_bits([int(coordinate_number)], "big", 21)


def __earth_reference_group(
    true_track: int, ground_speed: int, vertical_rate: int
) -> list[int]:
    true_track_number = int(true_track / (180 / 2**11))
    ground_speed_number = int(ground_speed / 0.5)
    vertical_rate_number = int(vertical_rate / 16)
    return __get_reference_group(
        true_track_number, ground_speed_number, vertical_rate_number
    )


def down_earth_reference_group(
    true_track: int, ground_speed: int, vertical_rate: int
) -> bytes:
    return to_bytes(
        to_bits([14], "big", 8)
        + __earth_reference_group(true_track, ground_speed, vertical_rate)
    )


def down_basic_report(
    lat: float, long: float, alt: int, time_stamp, redundancy, accuracy, tcas
) -> bytes:
    return to_bytes(
        to_bits([7], "big", 8)
        + __get_basic_report(lat, long, alt, time_stamp, redundancy, accuracy, tcas)
    )


def __predicted_route_group(
    lat: float,
    long: float,
    alt: int,
    eta: int,
    next_lat: float,
    next_long: float,
    next_alt: int,
):
    return (
        __get_coordinate(lat)
        + __get_coordinate(long)
        + [0]
        + to_bits([int(alt / 4)], "big", 15)
        + to_bits([eta], "big", 14)
        + __get_coordinate(next_lat)
        + __get_coordinate(next_long)
        + [0]
        + to_bits([int(next_alt / 4)], "big", 15)
        + [0] * 6
    )


def down_predicted_route_group(
    lat: float,
    long: float,
    alt: int,
    eta: int,
    next_lat: float,
    next_long: float,
    next_alt: int,
) -> bytes:
    return to_bytes(
        to_bits([13], "big", 8)
        + __predicted_route_group(lat, long, alt, eta, next_lat, next_long, next_alt)
    )


def down_emergency_basic_report(
    lat: float, long: float, alt: int, time_stamp, redundancy, accuracy, tcas
) -> bytes:
    return to_bytes(
        to_bits([9], "big", 8)
        + __get_basic_report(lat, long, alt, time_stamp, redundancy, accuracy, tcas)
    )


def __get_basic_report(
    lat: float, long: float, alt: int, time_stamp, redundancy, accuracy, tcas
) -> list[int]:
    lat_bits = __get_coordinate(lat)
    long_bits = __get_coordinate(long)

    time_minutes = time_stamp[0]
    time_seconds = time_stamp[1]
    time_number = int((time_minutes * 60 + time_seconds) * 8)

    return (
        lat_bits
        + long_bits
        + [0]
        + to_bits([int(alt / 4)], "big", 15)
        + to_bits([time_number], "big", 15)
        + __get_figure_of_merit(redundancy, accuracy, tcas)
    )


def down_intermediate_projected_intent_group(
    distance: int, track: int, alt: int, time: int
) -> bytes:
    distance_number = int(distance / 0.125)
    track_number = int(track / (180 / 2**11))
    altitude_number = int(alt / 4)

    return to_bytes(
        to_bits([22], "big", 8)
        + to_bits([distance_number], "big", 16)
        + [0]
        + to_bits([track_number], "big", 12)
        + [0]
        + to_bits([altitude_number], "big", 15)
        + to_bits([time], "big", 14)
        + [0] * 5
    )


def down_fixed_projected_intent_group(
    lat: float, long: float, alt: int, time_stamp
) -> bytes:
    time_minutes = time_stamp[0]
    time_seconds = time_stamp[1]
    time_number = time_minutes * 60 + time_seconds

    return to_bytes(
        to_bits([23], "big", 8)
        + __get_coordinate(lat)
        + __get_coordinate(long)
        + [0]
        + to_bits([int(alt / 4)], "big", 15)
        + to_bits([time_number], "big", 14)
    )


def down_vertical_change_even(
    lat: float,
    long: float,
    alt: int,
    time_stamp,
    redundancy,
    accuracy,
    tcas,
    true_track: int,
    ground_speed: int,
    vertical_rate: int,
):
    return to_bytes(
        to_bits([18], "big", 8)
        + __get_basic_report(lat, long, alt, time_stamp, redundancy, accuracy, tcas)
        + __earth_reference_group(true_track, ground_speed, vertical_rate)
    )


def down_altitude_change_event(lat, long, alt, time_stamp, redundancy, accuracy, tcas):
    return to_bytes(
        to_bits([19], "big", 8)
        + __get_basic_report(lat, long, alt, time_stamp, redundancy, accuracy, tcas)
    )


def down_waypoint_change_event(
    lat,
    long,
    alt,
    time_stamp,
    redundancy,
    accuracy,
    tcas,
    next_lat: float,
    next_long: float,
    next_alt: int,
    eta: int,
    next_next_lat: float,
    next_next_long: float,
    next_next_alt: int,
):
    return to_bytes(
        to_bits([20], "big", 8)
        + __get_basic_report(lat, long, alt, time_stamp, redundancy, accuracy, tcas)
        + __predicted_route_group(
            next_lat,
            next_long,
            next_alt,
            eta,
            next_next_lat,
            next_next_long,
            next_next_alt,
        )
    )
