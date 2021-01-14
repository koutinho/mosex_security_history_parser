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

    @patch('request_provider.requests')
    def test_get_price_sheet_none_bad_response_codes(self, mock_request):
        bad_response_codes = [100, 400, 500, 502]

        for bad_response_code in bad_response_codes:
            response_mock = Mock()
            response_mock.status_code = bad_response_code
            mock_request.get.return_value = response_mock
            r = get_price_sheet('AFLT', 1000, datetime.datetime(2015, 11, 20))
            assert r == None

    @patch('request_provider.requests')
    def test_get_price_sheet_json_on_success(self, mock_request):
        response_mock = Mock()
        response_mock.status_code = 200
        mock_request.get.return_value = response_mock
        response_mock.json.return_value = 'json content'

        json = get_price_sheet('AFLT', 1000, datetime.datetime(2015, 11, 20))
        response_mock.json.assert_called_once()
        assert json == 'json content'
