from __future__ import annotations

import json
import unittest
from pathlib import Path

from outfit_prompt import make_plan


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "outfit_config.json").read_text(encoding="utf-8"))


def weather(day: str, high: float, code: int = 0, rain: int = 0, wind: int = 5) -> dict:
    return {
        "date": day,
        "weather_code": code,
        "temperature_2m_max": high,
        "temperature_2m_min": high - 8,
        "apparent_temperature_max": high,
        "precipitation_probability_max": rain,
        "wind_speed_10m_max": wind,
    }


class OutfitPlanTests(unittest.TestCase):
    def test_hot_summer_uses_light_clothing(self) -> None:
        plan = make_plan(CONFIG, weather("2026-07-16", 34))
        self.assertEqual(plan["season"], "夏")
        self.assertEqual(plan["temperature_rule"], "真夏日")
        self.assertIn("半袖", plan["outfit"])

    def test_rain_adds_umbrella(self) -> None:
        plan = make_plan(CONFIG, weather("2026-06-20", 24, code=63, rain=90))
        self.assertTrue(any("傘" in addition for addition in plan["weather_additions"]))

    def test_christmas_overrides_normal_outfit_but_keeps_rain_modifier(self) -> None:
        plan = make_plan(CONFIG, weather("2026-12-25", 11, code=61, rain=80))
        self.assertEqual(plan["event"], "クリスマス")
        self.assertIn("クリスマス", plan["outfit"])
        self.assertTrue(any("傘" in addition for addition in plan["weather_additions"]))

    def test_new_year_uses_kimono(self) -> None:
        plan = make_plan(CONFIG, weather("2027-01-02", 9))
        self.assertEqual(plan["event"], "お正月")
        self.assertIn("振袖", plan["outfit"])


if __name__ == "__main__":
    unittest.main()
