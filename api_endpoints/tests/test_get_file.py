import unittest
#from tests.shared.default_events import get_example_event
import get_file

class TestGetFile(unittest.TestCase):
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
        event = None
        response = get_file.handler(event, None)
        self.assertEqual(response["statusCode"], 200)

