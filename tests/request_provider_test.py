import unittest
from request_provider import get_price_sheet
from request_provider import get_candles
from requests.exceptions import Timeout
from unittest.mock import patch
from unittest.mock import Mock
from parameterized import parameterized
import datetime
import json

class TestRequestProvider(unittest.TestCase):
    @patch('request_provider.requests')
    def test_get_price_sheet_request_url(self, mock_request):
        expected_url = "https://iss.moex.com/cs/engines/stock/markets/shares/boardgroups/57/securities/AFLT.json"
        expected_till_date = datetime.date(2015, 11, 20)
        get_price_sheet('AFLT', 1000, expected_till_date)
        
        payload = {'s1.type': 'candles', 'interval': '1', 'candles': 1000, 'till': expected_till_date}
        mock_request.get.assert_called_once_with(expected_url, params = payload)

    @patch('request_provider.requests')
    def test_get_price_sheet_timeout(self, mock_request):
        mock_request.get.side_effect = Timeout
        with self.assertRaises(Timeout):
            get_price_sheet('AFLT', 1000, datetime.date(2015, 11, 20))

    @patch('request_provider.requests')
    def test_get_price_sheet_none_bad_response_codes(self, mock_request):
        bad_response_codes = [100, 400, 500, 502]

        for bad_response_code in bad_response_codes:
            response_mock = Mock()
            response_mock.status_code = bad_response_code
            mock_request.get.return_value = response_mock
            r = get_price_sheet('AFLT', 1000, datetime.date(2015, 11, 20))
            assert r == None

    @patch('request_provider.requests')
    def test_get_price_sheet_json_on_success(self, mock_request):
        response_mock = Mock()
        response_mock.status_code = 200
        mock_request.get.return_value = response_mock
        response_mock.json.return_value = 'json content'

        json = get_price_sheet('AFLT', 1000, datetime.date(2015, 11, 20))
        response_mock.json.assert_called_once()
        assert json == 'json content'

    def test_get_candles_calls_get_price_sheet(self):
        with patch('request_provider.get_price_sheet') as mock_get_price_sheet:
            get_candles('AFLT', datetime.date(2015, 11, 20))
            mock_get_price_sheet.assert_called_once_with('AFLT', 1000, datetime.date(2015, 11, 21))

    def test_get_candles_return_filtered_candle_list(self):
        with patch('request_provider.get_price_sheet') as mock_get_price_sheet:
            json_string = """
            {
                "canvas": {
                },
                "zones": [
                    {
                        "left": 50,
                        "title": {
                        },
                        "series": [
                            {
                                "id": "s1",
                                "type": "candles",
                                "candles": [
                                    {
                                        "open_time": 1447830060000,
                                        "close_time": 1447830119000,
                                        "open": 54.79,
                                        "close": 54.84,
                                        "high": 54.84,
                                        "low": 54.77,
                                        "open_time_x": 53,
                                        "open_y": 330,
                                        "close_y": 326,
                                        "high_y": 326,
                                        "low_y": 332
                                    },
                                    {
                                        "open_time": 1447830120000,
                                        "close_time": 1447830179000,
                                        "open": 54.82,
                                        "close": 55,
                                        "high":55,
                                        "low": 54.78,
                                        "open_time_x": 54,
                                        "open_y": 327,
                                        "close_y": 313,
                                        "high_y": 313,
                                        "low_y": 331
                                    },
                                    {
                                        "open_time": 1447830180000,
                                        "close_time": 1447830239000,
                                        "open": 54.91,
                                        "close": 55,
                                        "high": 55,
                                        "low": 54.91,
                                        "open_time_x": 54,
                                        "open_y": 320,
                                        "close_y": 313,
                                        "high_y": 313,
                                        "low_y": 320
                                    },
                                    {
                                        "open_time": 1611580644000,
                                        "close_time": 1611580704000,
                                        "open": 54.91,
                                        "close": 55,
                                        "high": 55,
                                        "low": 54.91,
                                        "open_time_x": 54,
                                        "open_y": 320,
                                        "close_y": 313,
                                        "high_y": 313,
                                        "low_y": 320
                                    },
                                    {
                                        "open_time": 1612012704000,
                                        "close_time": 1612012764000,
                                        "open": 54.91,
                                        "close": 55,
                                        "high": 55,
                                        "low": 54.91,
                                        "open_time_x": 54,
                                        "open_y": 320,
                                        "close_y": 313,
                                        "high_y": 313,
                                        "low_y": 320
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            """
            data = json.loads(json_string)
            mock_get_price_sheet.return_value = data
            candles = get_candles('AFLT', datetime.date(2015, 11, 18))

            assert len(candles) == 3
            assert all(map(lambda x: x.open_time.date() == datetime.date(2015, 11, 18), candles))
