from __future__ import annotations

import argparse
import os
import time

import requests


PUSH_URL = "https://api.line.me/v2/bot/message/push"


def wait_for_image(url: str) -> None:
    for attempt in range(10):
        try:
            response = requests.get(url, timeout=20)
            if response.ok and response.headers.get("content-type", "").startswith("image/"):
                return
        except requests.RequestException:
            pass
        time.sleep(min(5 + attempt * 3, 30))
    raise RuntimeError(f"画像URLを確認できませんでした: {url}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image_url")
    args = parser.parse_args()

    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    to = os.environ["LINE_TO"]
    wait_for_image(args.image_url)

    payload = {
        "to": to,
        "messages": [
            {
                "type": "image",
                "originalContentUrl": args.image_url,
                "previewImageUrl": args.image_url,
            }
        ],
    }
    response = requests.post(
        PUSH_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    print("LINEへ送信しました")


if __name__ == "__main__":
    main()
