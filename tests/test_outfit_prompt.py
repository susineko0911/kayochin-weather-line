from __future__ import annotations

import json
import unittest
from pathlib import Path

from outfit_prompt import make_plan, make_prompt, resolve_reference_path


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

    def test_prompt_requires_identity_reference(self) -> None:
        prompt = make_prompt(CONFIG, weather("2026-04-10", 21))
        self.assertIn(str(Path("assets/reference/kayochin_reference.png")), prompt)
        self.assertIn("参照画像と同じ顔立ち", prompt)
        self.assertIn("服装、手に持つ小物、背景だけ", prompt)

    def test_prompt_contains_template_specific_identity_traits(self) -> None:
        prompt = make_prompt(CONFIG, weather("2026-04-10", 21))
        self.assertIn("濃い茶色のツインテール", prompt)
        self.assertIn("赤い髪リボン", prompt)
        self.assertIn("暖かい茶色の瞳", prompt)

    def test_reference_path_is_relative_to_config(self) -> None:
        config_path = ROOT / "outfit_config.json"
        resolved = resolve_reference_path(config_path, "assets/reference/kayochin_reference.png")
        self.assertEqual(resolved, ROOT / "assets/reference/kayochin_reference.png")


if __name__ == "__main__":
    unittest.main()
