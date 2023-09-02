import unittest
from adsc_spoofer import up_cancel_all_contracts, to_bits, up_cancel_contract, up_cancel_emergency_mode, up_periodic_contract, up_event_contract, down_basic_report, down_flight_identification_group, down_earth_reference_group, down_air_reference_group, down_meterological_group, down_predicted_route_group, down_emergency_basic_report, down_noncompliance, down_intermediate_projected_intent_group, down_fixed_projected_intent_group, down_acknowledgement, down_negative_acknowledgement, down_cancel_emergency_mode


class TestUplink(unittest.TestCase):
    """Test encoding examples found in ARINC-745 attachment 8-3"""

    def test_cancel_all_contracts(self):
        self.assertEqual(to_bits(up_cancel_all_contracts(), "big"), [
                         0, 0, 0, 0, 0, 0, 0, 1])

    def test_cancel_contract(self):
        self.assertEqual(to_bits(up_cancel_contract(17), "big"), [
                         0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1])

    def test_cancel_emergency_mode(self):
        self.assertEqual(to_bits(up_cancel_emergency_mode(255), "big"), [
                         0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1])

    def test_default_periodic_contract(self):
        self.assertEqual(to_bits(up_periodic_contract(0), "big"), [
                         0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0])

    def test_complex_periodic_contract(self):
        self.assertEqual(to_bits(up_periodic_contract(1, flight_id_group=5), "big"), [
                         0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1])

    def test_waypoint_change_event_contract(self):
        self.assertEqual(to_bits(up_event_contract(2, waypoint_change=True), "big"), [
                         0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0])

    def test_multiple_event_contracts(self):
        self.assertEqual(to_bits(up_event_contract(3, waypoint_change=True, altitude_range={"ceiling": int(15000/4), "floor": int(21000/4)}), "big"), [
                         0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0])


class TestDowlink(unittest.TestCase):
    """Test encoding examples found in ARINC-745 attachment 8-3"""

    def test_basic_report(self):
        self.assertEqual(to_bits(down_basic_report(36.1982346, -95.8883286, 14480, (48, 35), 1, 7, 0), "big"), [
            0, 0, 0, 0, 0, 1, 1, 1,
            0, 0, 0, 1, 1, 0, 0, 1,
            1, 0, 1, 1, 1, 1, 0, 1,
            1, 0, 1, 1, 0, 1, 0, 1,
            1, 1, 0, 1, 1, 1, 1, 0,
            1, 0, 0, 0, 0, 0, 0, 0,
            1, 0, 0, 0, 0, 0, 1, 1,
            1, 0, 0, 0, 1, 0, 0, 1,
            0, 0, 1, 0, 1, 1, 0, 1,
            1, 0, 0, 0, 1, 1, 0, 0,
            0, 0, 0, 0, 1, 1, 1, 1
        ])

    def test_flight_identification_group(self):
        self.assertEqual(to_bits(down_flight_identification_group("AAL247"), "big"), [
            0, 0, 0, 0, 1, 1, 0, 0,
            0, 0, 0, 0, 0, 1, 0, 0,
            0, 0, 0, 1, 0, 0, 1, 1,
            0, 0, 1, 1, 0, 0, 1, 0,
            1, 1, 0, 1, 0, 0, 1, 1,
            0, 1, 1, 1, 1, 0, 0, 0,
            0, 0, 1, 0, 0, 0, 0, 0
        ])

    def test_earth_reference_group(self):
        self.assertEqual(to_bits(down_earth_reference_group(248, 210, 1750), "big"), [
            0, 0, 0, 0, 1, 1, 1, 0,
            0, 1, 0, 1, 1, 0, 0, 0,
            0, 0, 1, 0, 1, 0, 0, 0,
            0, 1, 1, 0, 1, 0, 0, 1,
            0, 0, 0, 0, 0, 0, 0, 1,
            1, 0, 1, 1, 0, 1, 0, 0
        ])

    def test_air_reference_group(self):
        self.assertEqual(to_bits(down_air_reference_group(248, 0.8, -100), "big"), [
            0, 0, 0, 0, 1, 1, 1, 1,
            0, 1, 0, 1, 1, 0, 0, 0,
            0, 0, 1, 0, 1, 0, 0, 1,
            1, 0, 0, 1, 0, 0, 0, 0,
            0, 0, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 0, 1, 0, 0, 0,
        ])

    def test_meterological_group(self):
        self.assertEqual(to_bits(down_meterological_group(40, 122, -20), "big"), [
            0, 0, 0, 1, 0, 0, 0, 0,
            0, 0, 1, 0, 1, 0, 0, 0,
            0, 0, 0, 1, 0, 1, 0, 1,
            1, 0, 1, 1, 1, 1, 1, 1,
            0, 1, 1, 0, 0, 0, 0, 0
        ])

    def test_predicted_route_group(self):
        self.assertEqual(to_bits(down_predicted_route_group(33.94339, 118.4065247, 33000, 304, -41.9799614, -87.9048729, 23000), "big"), [
            0, 0, 0, 0, 1, 1, 0, 1,
            0, 0, 0, 1, 1, 0, 0, 0,
            0, 0, 1, 0, 0, 0, 1, 1,
            0, 0, 1, 1, 0, 0, 1, 0,
            1, 0, 1, 0, 0, 0, 0, 1,
            1, 0, 0, 1, 1, 0, 1, 0,
            0, 0, 0, 0, 1, 0, 0, 0,
            0, 0, 0, 0, 1, 1, 1, 0,
            1, 0, 0, 0, 0, 0, 0, 1,
            0, 0, 1, 1, 0, 0, 0, 0,
            1, 1, 1, 0, 0, 0, 1, 0,
            0, 0, 1, 0, 0, 1, 0, 1,
            1, 1, 0, 0, 1, 1, 1, 0,
            0, 0, 0, 0, 1, 0, 1, 1,
            1, 1, 1, 0, 1, 0, 1, 1,
            0, 1, 0, 0, 0, 1, 0, 1,
            1, 0, 0, 1, 1, 1, 0, 1,
            1, 0, 0, 0, 0, 0, 0, 0
        ])

    def test_emergency_basic_report(self):
        self.assertEqual(to_bits(down_emergency_basic_report(-36.1982346, 95.8883286, 14480, (59, 59.875), 0, 1, 0), "big"), [
            0, 0, 0, 0, 1, 0, 0, 1,
            1, 1, 1, 0, 0, 1, 1, 0,
            0, 1, 0, 0, 0, 0, 1, 0,
            0, 1, 0, 1, 0, 0, 1, 0,
            0, 0, 1, 0, 0, 0, 0, 1,
            0, 1, 1, 1, 1, 1, 1, 1,
            1, 0, 0, 0, 0, 0, 1, 1,
            1, 0, 0, 0, 1, 0, 0, 1,
            0, 0, 1, 1, 1, 0, 0, 0,
            0, 0, 1, 1, 1, 1, 1, 1,
            1, 0, 0, 0, 0, 0, 1, 0
        ])

    def test_noncompliance_notification(self):
        self.assertEqual(to_bits(down_noncompliance(8, [{
            "group_tag": 13,
            "group_undefined": False,
            "unavailable_params": [4, 5, 6]
        }, {
            "group_tag": 27,
            "group_undefined": True,
        }]), "big"), [
            0, 0, 0, 0, 0, 1, 0, 1,
            0, 0, 0, 0, 1, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 1, 0,
            0, 0, 0, 0, 1, 1, 0, 1,
            0, 0, 0, 0, 0, 0, 1, 1,
            0, 1, 0, 0, 0, 1, 0, 1,
            0, 1, 1, 0, 0, 0, 0, 0,
            0, 0, 0, 1, 1, 0, 1, 1,
            1, 0, 0, 0, 0, 0, 0, 0
        ])

    def test_intermediate_projected_intent_group(self):
        self.assertEqual(to_bits(down_intermediate_projected_intent_group(25, 248, 23000, 304), "big"), [
            0, 0, 0, 1, 0, 1, 1, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            1, 1, 0, 0, 1, 0, 0, 0,
            0, 1, 0, 1, 1, 0, 0, 0,
            0, 0, 1, 0, 1, 0, 0, 0,
            1, 0, 1, 1, 0, 0, 1, 1,
            1, 0, 1, 1, 0, 0, 0, 0,
            0, 0, 1, 0, 0, 1, 1, 0,
            0, 0, 0, 0, 0, 0, 0, 0
        ])

    def test_fixed_projected_intent_group(self):
        self.assertEqual(to_bits(down_fixed_projected_intent_group(33.94339, -87.9048729, 35000, (20, 0)), "big"), [
            0, 0, 0, 1, 0, 1, 1, 1,
            0, 0, 0, 1, 1, 0, 0, 0,
            0, 0, 1, 0, 0, 0, 1, 1,
            0, 0, 1, 1, 0, 1, 1, 0,
            0, 0, 0, 0, 1, 0, 1, 1,
            1, 1, 1, 0, 1, 0, 1, 1,
            0, 1, 0, 0, 1, 0, 0, 0,
            1, 0, 0, 0, 1, 0, 1, 1,
            1, 0, 0, 0, 0, 1, 0, 0,
            1, 0, 1, 1, 0, 0, 0, 0
        ])

    def test_acknowledgement(self):
        self.assertEqual(to_bits(down_acknowledgement(5), "big"), [
            0, 0, 0, 0, 0, 0, 1, 1,
            0, 0, 0, 0, 0, 1, 0, 1
        ])

    def test_negative_acknowledgement1(self):
        self.assertEqual(to_bits(down_negative_acknowledgement(19, 2, 18), "big"), [
            0, 0, 0, 0, 0, 1, 0, 0,
            0, 0, 0, 1, 0, 0, 1, 1,
            0, 0, 0, 0, 0, 0, 1, 0,
            0, 0, 0, 1, 0, 0, 1, 0
        ])

    def test_negative_acknowledgement2(self):
        self.assertEqual(to_bits(down_negative_acknowledgement(6, 4), "big"), [
            0, 0, 0, 0, 0, 1, 0, 0,
            0, 0, 0, 0, 0, 1, 1, 0,
            0, 0, 0, 0, 0, 1, 0, 0,
        ])

    def test_cancel_emergency_mode(self):
        self.assertEqual(to_bits(down_cancel_emergency_mode(), "big"), [
            0, 0, 0, 0, 0, 1, 1, 0,
        ])


class TestReportingRate(unittest.TestCase):
    """Test encoding examples found in ARINC-745 attachment 8-4"""

    def test_demand_mode_request(self):
        self.assertEqual(to_bits(up_periodic_contract(1, reporting_intervalal_tag={"sf": 0, "rate": 1}), "big"), [
                         0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1])

    def test_second_interval(self):
        self.assertEqual(to_bits(up_periodic_contract(1, reporting_intervalal_tag={"sf": 1, "rate": 0}), "big"), [
                         0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0])

    def test_304_seconds_interval(self):
        self.assertEqual(to_bits(up_periodic_contract(1, reporting_intervalal_tag={"sf": 2, "rate": 37}), "big"), [
                         0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1])

    def test_hour_interval(self):
        self.assertEqual(to_bits(up_periodic_contract(1, reporting_intervalal_tag={"sf": 3, "rate": 55}), "big"), [
                         0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1])


if __name__ == '__main__':
    unittest.main()
