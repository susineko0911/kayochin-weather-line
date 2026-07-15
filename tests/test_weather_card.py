from __future__ import annotations

import unittest

from weather_card import current_weather_summary


class CurrentWeatherSummaryTests(unittest.TestCase):
    def test_uses_current_observation(self) -> None:
        weather = {
            "weather_code": 2,
            "temperature_2m_max": 34,
            "apparent_temperature_max": 41,
            "current_weather_code": 63,
            "current_temperature_2m": 26.4,
            "current_apparent_temperature": 29.2,
        }
        self.assertEqual(current_weather_summary(weather), ("雨", 26, 29))

    def test_falls_back_to_daily_values(self) -> None:
        weather = {
            "weather_code": 2,
            "temperature_2m_max": 34,
            "apparent_temperature_max": 41,
        }
        self.assertEqual(current_weather_summary(weather), ("晴れ時々くもり", 34, 41))


if __name__ == "__main__":
    unittest.main()
