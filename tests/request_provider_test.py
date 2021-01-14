import unittest
from request_provider import get_price_sheet
from requests.exceptions import Timeout
from unittest.mock import patch
from unittest.mock import Mock
from parameterized import parameterized
import datetime

class TestRequestProvider(unittest.TestCase):
    @patch('request_provider.requests')
    def test_get_price_sheet_request_url(self, mock_request):
        expected_url = "https://iss.moex.com/cs/engines/stock/markets/shares/boardgroups/57/securities/AFLT.json"
        expected_till_date = datetime.datetime(2015, 11, 20)
        get_price_sheet('AFLT', 1000, expected_till_date)
        
        payload = {'s1.type': 'candles', 'interval': '1', 'candles': 1000, 'till': expected_till_date}
        mock_request.get.assert_called_once_with(expected_url, params = payload)

    @patch('request_provider.requests')
    def test_get_price_sheet_timeout(self, mock_request):
        mock_request.get.side_effect = Timeout
        with self.assertRaises(Timeout):
            get_price_sheet('AFLT', 1000, datetime.datetime(2015, 11, 20))

    # @parameterized.expand([
    #     (100), (400), (500), (502)
    # ])
    # @patch('request_provider.requests')
    # def test_get_price_sheet_none_if_return_code_is_not_200(self, bad_return_code, mock_request):
    #     response_mock = Mock()
    #     response_mock.status_code = bad_return_code
    #     mock_request.get.return_value = response_mock
    #     r = get_price_sheet('AFLT', 1000, datetime.datetime(2015, 11, 20))
    #     assert r == None