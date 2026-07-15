from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps


LATITUDE = 35.72526
LONGITUDE = 139.53830
LOCATION = "東京都 西東京市"
CANVAS = (1200, 1200)
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_LABELS = {
    0: "快晴",
    1: "晴れ",
    2: "晴れ時々くもり",
    3: "くもり",
    45: "霧",
    48: "霧",
    51: "弱い霧雨",
    53: "霧雨",
    55: "強い霧雨",
    56: "着氷性の霧雨",
    57: "強い着氷性の霧雨",
    61: "弱い雨",
    63: "雨",
    65: "強い雨",
    66: "着氷性の雨",
    67: "強い着氷性の雨",
    71: "弱い雪",
    73: "雪",
    75: "強い雪",
    77: "雪あられ",
    80: "弱いにわか雨",
    81: "にわか雨",
    82: "激しいにわか雨",
    85: "弱いにわか雪",
    86: "強いにわか雪",
    95: "雷雨",
    96: "ひょうを伴う雷雨",
    99: "激しいひょう・雷雨",
}


def fetch_weather() -> dict:
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "daily": ",".join(
            [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "precipitation_probability_max",
                "wind_speed_10m_max",
            ]
        ),
        "timezone": "Asia/Tokyo",
        "forecast_days": 1,
    }
    response = requests.get(FORECAST_URL, params=params, timeout=30)
    response.raise_for_status()
    daily = response.json()["daily"]
    return {key: values[0] for key, values in daily.items() if key != "time"} | {
        "date": daily["time"][0]
    }


def outfit_key(weather: dict) -> str:
    high = float(weather["temperature_2m_max"])
    rain = int(weather["precipitation_probability_max"] or 0)
    code = int(weather["weather_code"])
    if high < 10:
        temperature_key = "cold"
    elif high < 16:
        temperature_key = "cool"
    elif high < 23:
        temperature_key = "mild"
    elif high < 28:
        temperature_key = "warm"
    else:
        temperature_key = "hot"

    if rain >= 40 or 51 <= code <= 82:
        rain_band = "cold" if high < 16 else "mild" if high < 25 else "warm"
        return f"rain_{rain_band}"
    return temperature_key


def find_outfit(directory: Path, key: str) -> Path | None:
    candidates = [key]
    if key.startswith("rain_"):
        rain_band = key.removeprefix("rain_")
        candidates.append({"cold": "cool", "mild": "mild", "warm": "warm"}[rain_band])
    candidates.append("default")
    for stem in candidates:
        for suffix in (".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"):
            path = directory / f"{stem}{suffix}"
            if path.exists():
                return path
    return None


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    env_path = os.getenv("JAPANESE_FONT")
    candidates = [
        env_path,
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "C:/Windows/Fonts/YuGothB.ttc" if bold else "C:/Windows/Fonts/YuGothM.ttc",
        "C:/Windows/Fonts/meiryob.ttc" if bold else "C:/Windows/Fonts/meiryo.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default(size=size)


def base_image(outfit: Path | None) -> Image.Image:
    if outfit:
        with Image.open(outfit) as source:
            return ImageOps.fit(source.convert("RGB"), CANVAS, method=Image.Resampling.LANCZOS)
    image = Image.new("RGB", CANVAS, "#f4f0e8")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((150, 130, 1050, 880), radius=60, fill="#dfeee1")
    draw.text((600, 470), "服装画像を追加してね", font=font(58, True), fill="#48604c", anchor="mm")
    return image


def create_card(weather: dict, outfit: Path | None, output: Path) -> None:
    image = base_image(outfit).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((55, 780, 1145, 1140), radius=42, fill=(255, 255, 255, 225))
    draw.rounded_rectangle((55, 55, 590, 155), radius=30, fill=(255, 255, 255, 220))

    code = int(weather["weather_code"])
    high = round(float(weather["temperature_2m_max"]))
    low = round(float(weather["temperature_2m_min"]))
    feels = round(float(weather["apparent_temperature_max"]))
    rain = round(float(weather["precipitation_probability_max"] or 0))
    display_date = date.fromisoformat(weather["date"])

    draw.text((85, 105), f"{display_date.month}月{display_date.day}日  {LOCATION}", font=font(35, True), fill="#263238", anchor="lm")
    draw.text((100, 845), WEATHER_LABELS.get(code, "天気情報"), font=font(78, True), fill="#263238")
    draw.text((100, 950), f"最高 {high}℃   最低 {low}℃", font=font(55, True), fill="#263238")
    draw.text((100, 1035), f"体感 {feels}℃   降水確率 {rain}%", font=font(46), fill="#40515a")
    draw.text((1100, 1110), "Weather: Open-Meteo.com", font=font(24), fill="#607d8b", anchor="rs")

    output.parent.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(image, overlay).convert("RGB").save(output, "PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outfits", type=Path, default=Path("assets/outfits"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--outfit", type=Path, help="自動生成した当日用画像を直接指定")
    args = parser.parse_args()
    weather = fetch_weather()
    key = outfit_key(weather)
    outfit = args.outfit if args.outfit else find_outfit(args.outfits, key)
    output = args.output or Path("public") / f"{weather['date']}.png"
    create_card(weather, outfit, output)
    print(output.as_posix())


if __name__ == "__main__":
    main()
