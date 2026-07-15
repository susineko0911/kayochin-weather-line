from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from weather_card import WEATHER_LABELS, fetch_weather


RAIN_CODES = set(range(51, 68)) | set(range(80, 83)) | {95, 96, 99}
SNOW_CODES = set(range(71, 78)) | {85, 86}


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as source:
        return json.load(source)


def month_day(value: str) -> tuple[int, int]:
    month, day = value.split("-", maxsplit=1)
    return int(month), int(day)


def in_annual_range(target: tuple[int, int], start: tuple[int, int], end: tuple[int, int]) -> bool:
    if start <= end:
        return start <= target <= end
    return target >= start or target <= end


def find_event(config: dict, target_date: date) -> dict | None:
    target = (target_date.month, target_date.day)
    for event in config.get("events", []):
        if target in [month_day(value) for value in event.get("dates", [])]:
            return event
        if "start" in event and "end" in event:
            if in_annual_range(target, month_day(event["start"]), month_day(event["end"])):
                return event
    return None


def find_season(config: dict, target_date: date) -> dict:
    for season in config["seasons"]:
        if target_date.month in season["months"]:
            return season
    raise ValueError(f"月 {target_date.month} に対応する季節設定がありません")


def find_temperature_rule(config: dict, maximum: float) -> dict:
    for rule in config["temperature_rules"]:
        minimum_ok = maximum >= float(rule.get("min_c", float("-inf")))
        maximum_ok = maximum < float(rule.get("max_c_below", float("inf")))
        if minimum_ok and maximum_ok:
            return rule
    raise ValueError(f"最高気温 {maximum}℃ に対応する服装設定がありません")


def weather_additions(config: dict, weather: dict) -> list[dict]:
    code = int(weather["weather_code"])
    rain_probability = float(weather.get("precipitation_probability_max") or 0)
    wind = float(weather.get("wind_speed_10m_max") or 0)
    additions = []
    for modifier in config.get("weather_modifiers", []):
        condition = modifier["condition"]
        applies = (
            condition == "rain"
            and (rain_probability >= float(modifier.get("rain_probability_at_least", 101)) or code in RAIN_CODES)
        ) or (condition == "snow" and code in SNOW_CODES) or (
            condition == "wind" and wind >= float(modifier.get("wind_kmh_at_least", float("inf")))
        )
        if applies:
            additions.append(modifier)
    return additions


def make_plan(config: dict, weather: dict) -> dict:
    target_date = date.fromisoformat(weather["date"])
    maximum = float(weather["temperature_2m_max"])
    season = find_season(config, target_date)
    temperature = find_temperature_rule(config, maximum)
    event = find_event(config, target_date)
    modifiers = weather_additions(config, weather)
    return {
        "date": target_date.isoformat(),
        "season": season["name"],
        "temperature_rule": temperature["name"],
        "event": event["name"] if event else None,
        "outfit": event["outfit"] if event else temperature["outfit"],
        "season_detail": season["detail"],
        "scene": event.get("scene", "その日の天気が自然に伝わる屋外背景") if event else "その日の天気が自然に伝わる屋外背景",
        "weather_additions": [modifier["addition"] for modifier in modifiers],
    }


def make_prompt(config: dict, weather: dict) -> str:
    plan = make_plan(config, weather)
    character = config["character"]
    identity_rules = "。".join(character.get("identity_rules", []))
    code = int(weather["weather_code"])
    additions = "。".join(plan["weather_additions"]) or "特別な天候小物は不要"
    constraints = "。".join(config["generation_constraints"])
    event_line = plan["event"] or "通常の日"
    return "\n".join(
        [
            "Use case: illustration-story",
            "Asset type: 毎朝LINEで送る天気カードの人物背景画像",
            f"Primary request: {character['name']}が今日の天気に合う服装で出かける1枚絵",
            f"Input images: {character['reference_image']} を人物同一性の基準画像として使用",
            f"Subject: {character['appearance']}",
            f"Identity preservation: {identity_rules}",
            f"Style/medium: {character['image_style']}",
            f"Date/event: {plan['date']}、{event_line}",
            f"Weather context: {WEATHER_LABELS.get(code, '天気')}、最高{weather['temperature_2m_max']}℃、最低{weather['temperature_2m_min']}℃、降水確率{weather.get('precipitation_probability_max', 0)}%",
            f"Outfit: {plan['outfit']}。{plan['season_detail']}",
            f"Weather accessories: {additions}",
            f"Scene/backdrop: {plan['scene']}",
            "Composition/framing: 人物の全身を中央から少し上に配置し、服装が明確に見える",
            f"Constraints: {constraints}",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("outfit_config.json"))
    parser.add_argument("--weather-json", type=Path)
    parser.add_argument("--plan-json", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    reference_path = Path(config["character"]["reference_image"])
    if not reference_path.exists():
        print(
            f"注意: 基準画像がありません: {reference_path}。画像生成前に配置してください。",
            file=sys.stderr,
        )
    if args.weather_json:
        with args.weather_json.open("r", encoding="utf-8") as source:
            weather = json.load(source)
    else:
        weather = fetch_weather()
    if args.plan_json:
        print(json.dumps(make_plan(config, weather), ensure_ascii=False, indent=2))
    else:
        print(make_prompt(config, weather))


if __name__ == "__main__":
    main()
