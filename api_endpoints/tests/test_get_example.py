import unittest
from tests.shared.default_events import get_example_event
import get_example

class TestGetExample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_get_200_response(self):
        event = get_example_event()
        response = get_example.handler(event, None)
        self.assertEqual(response["statusCode"], 200)

