import unittest

from adsc_spoofer import up_cancel_contract, get_acars_message


class TestAcars(unittest.TestCase):
    def test_get_acars_message(self):
        adsc_message = up_cancel_contract(0)
        acars_message = get_acars_message(
            adsc_message, ".9XR-WP", "BZVCAYA", "W")
        self.assertEqual(acars_message.hex(
        ), "ffff0132aeb95852ad57d015c1b657022fc2dad643c1d9c1aec1c4d3aeb95852ad57d0b032b0b0b9c232b60d8a83b3a97f")


if __name__ == '__main__':
    unittest.main()
