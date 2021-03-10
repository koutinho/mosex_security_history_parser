import os, unittest, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from request_provider import get_candles_sheet_async, get_candles_async, get_candles_for_month
from requests.exceptions import Timeout
from unittest.mock import patch, Mock
from parameterized import parameterized
import datetime, json, asyncio, pytest
from candle import Candle

class TestClass:
    @pytest.mark.asyncio
    @patch('request_provider.requests')
    async def test_get_candles_sheet_async_request_url(self, mock_request):
        expected_url = "https://iss.moex.com/cs/engines/stock/markets/shares/boardgroups/57/securities/AFLT.json"
        expected_till_date = datetime.date(2015, 11, 20)

        await get_candles_sheet_async('AFLT', 1000, expected_till_date)
        
        payload = {'s1.type': 'candles', 'interval': '1', 'candles': 1000, 'till': expected_till_date}
        mock_request.get.assert_called_once_with(expected_url, params = payload)

    @pytest.mark.asyncio
    @patch('request_provider.requests')
    async def test_get_candles_sheet_async_timeout(self, mock_request):
        mock_request.get.side_effect = Timeout
        with pytest.raises(Timeout):
            await get_candles_sheet_async('AFLT', 1000, datetime.date(2015, 11, 20))

    @pytest.mark.asyncio
    @patch('request_provider.requests')
    async def test_get_candles_sheet_async_none_bad_response_codes(self, mock_request):
        bad_response_codes = [100, 400, 500, 502]

        for bad_response_code in bad_response_codes:
            response_mock = Mock()
            response_mock.status_code = bad_response_code
            mock_request.get.return_value = response_mock
            r = await get_candles_sheet_async('AFLT', 1000, datetime.date(2015, 11, 20))
            assert r == None

    @pytest.mark.asyncio
    @patch('request_provider.requests')
    async def test_get_price_sheet_json_on_success(self, mock_request):
        response_mock = Mock()
        response_mock.status_code = 200
        mock_request.get.return_value = response_mock
        response_mock.json.return_value = 'json content'

        json = await get_candles_sheet_async('AFLT', 1000, datetime.date(2015, 11, 20))
        response_mock.json.assert_called_once()
        assert json == 'json content'

    @pytest.mark.asyncio
    async def test_get_candles_calls_get_price_sheet(self):
        with patch('request_provider.get_candles_sheet_async') as get_candles_sheet_async:
            await get_candles_async('AFLT', datetime.date(2015, 11, 20))
            get_candles_sheet_async.assert_called_once_with('AFLT', 1000, datetime.date(2015, 11, 21))

    @pytest.mark.asyncio
    async def test_get_candles_return_filtered_candle_list(self):
        with patch('request_provider.get_candles_sheet_async') as mock_get_candles_sheet_async:
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
            mock_get_candles_sheet_async.return_value = data
            candles = await get_candles_async('AFLT', datetime.date(2015, 11, 18))

            assert len(candles) == 3
            assert all(map(lambda x: x.open_time.date() == datetime.date(2015, 11, 18), candles))

    @pytest.mark.asyncio
    async def test_get_candles_for_month_call_get_candles_async_with_month_days(self):
        with patch('request_provider.get_candles_async') as mock_get_candles_async, patch('request_provider.monthrange') as mock_monthrange:
            mock_monthrange.return_value = (1, 3)
            await get_candles_for_month('AFLT', 2020, 1)
            assert mock_get_candles_async.call_count == 3
            mock_get_candles_async.assert_any_call('AFLT', datetime.date(2020, 1, 1))
            mock_get_candles_async.assert_any_call('AFLT', datetime.date(2020, 1, 2))
            mock_get_candles_async.assert_any_call('AFLT', datetime.date(2020, 1, 3))

    @pytest.mark.asyncio
    async def test_get_candles_for_month_return_flattened_list_of_candles(self):
        with patch('request_provider.get_candles_async') as mock_get_candles_async, patch('request_provider.monthrange') as mock_monthrange:
            mock_monthrange.return_value = (1, 3)

            candle1 = Candle(228, 229, datetime.datetime(2020, 1, 1, 1, 1, 1), datetime.datetime(2020, 1, 1, 1, 1, 1), 228, 228)
            candle2 = Candle(229, 230, datetime.datetime(2020, 1, 1, 1, 1, 1), datetime.datetime(2020, 1, 1, 1, 1, 1), 228, 228)
            candle3 = Candle(230, 231, datetime.datetime(2020, 1, 1, 1, 1, 1), datetime.datetime(2020, 1, 1, 1, 1, 1), 228, 228)
            candle4 = Candle(231, 232, datetime.datetime(2020, 1, 1, 1, 1, 1), datetime.datetime(2020, 1, 1, 1, 1, 1), 228, 228)
            candle5 = Candle(232, 233, datetime.datetime(2020, 1, 1, 1, 1, 1), datetime.datetime(2020, 1, 1, 1, 1, 1), 228, 228)
            candle6 = Candle(233, 234, datetime.datetime(2020, 1, 1, 1, 1, 1), datetime.datetime(2020, 1, 1, 1, 1, 1), 228, 228)
            candle7 = Candle(234, 235, datetime.datetime(2020, 1, 1, 1, 1, 1), datetime.datetime(2020, 1, 1, 1, 1, 1), 228, 228)
            candle8 = Candle(235, 236, datetime.datetime(2020, 1, 1, 1, 1, 1), datetime.datetime(2020, 1, 1, 1, 1, 1), 228, 228)
            candle9 = Candle(236, 237, datetime.datetime(2020, 1, 1, 1, 1, 1), datetime.datetime(2020, 1, 1, 1, 1, 1), 228, 228)

            return_candles = [
                [candle1, candle2, candle3],
                [candle4, candle5],
                [candle6, candle7, candle8, candle9]
            ]

            mock_get_candles_async.side_effect  = return_candles

            candles = await get_candles_for_month('AFLT', 2020, 1)

            assert len(candles) == 9
            assert candle1 in candles
            assert candle2 in candles
            assert candle3 in candles
            assert candle4 in candles
            assert candle5 in candles
            assert candle6 in candles
            assert candle7 in candles
            assert candle8 in candles
            assert candle9 in candles
    
    @pytest.mark.asyncio
    async def test_get_candles_for_month_exception(self):
        with patch('request_provider.get_candles_async') as mock_get_candles_async, patch('request_provider.monthrange') as mock_monthrange:
            mock_monthrange.return_value = (1, 3)

            candle1 = Candle(228, 229, datetime.datetime(2020, 1, 1, 1, 1, 1), datetime.datetime(2020, 1, 1, 1, 1, 1), 228, 228)
            candle2 = Candle(229, 230, datetime.datetime(2020, 1, 1, 1, 1, 1), datetime.datetime(2020, 1, 1, 1, 1, 1), 228, 228)

            return_candles = [
                Timeout,
                [candle1],
                [candle2]
            ]

            mock_get_candles_async.side_effect  = return_candles

            candles = await get_candles_for_month('AFLT', 2020, 1)
            
            assert len(candles) == 2
            assert candle1 in candles
            assert candle2 in candles
