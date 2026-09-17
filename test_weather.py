import weather


class Response:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


def test_get_weather():
    payloads = iter((
        {"results": [{"latitude": 31.23, "longitude": 121.47}]},
        {"daily": {"temperature_2m_max": [25, 26, 27], "temperature_2m_min": [15, 16, 17], "precipitation_sum": [0, 1.2, 0], "weather_code": [0, 61, 3]}},
    ))
    original_get = weather.requests.get
    weather.requests.get = lambda *args, **kwargs: Response(next(payloads))
    try:
        assert weather.get_weather("Shanghai", "tomorrow") == {
            "max_temperature": 26, "min_temperature": 16, "precipitation": 1.2,
            "weather_condition": "slight rain", "need_umbrella": True,
        }
        assert "error" in weather.get_weather("Shanghai", "next_week")
    finally:
        weather.requests.get = original_get


if __name__ == "__main__":
    test_get_weather()
    print("ok")
