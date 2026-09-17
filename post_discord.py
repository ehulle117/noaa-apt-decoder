#!/usr/bin/env python3
"""Post an image to a Discord channel via the bot API.

Reads the bot token from ~/.config/noaa-apt-decoder/discord_bot_token
(never hardcoded, never logged).

Usage: python3 post_discord.py <channel_id> <image.png> [caption]
"""
import json
import subprocess
import sys
from pathlib import Path

TOKEN_FILE = Path.home() / ".config" / "noaa-apt-decoder" / "discord_bot_token"


def post(channel_id: str, image_path: str, caption: str = "") -> None:
    token = TOKEN_FILE.read_text().strip()
    subprocess.run(
        [
            "curl", "-sS", "-f",
            "-H", f"Authorization: Bot {token}",
            "-F", f"payload_json={json.dumps({'content': caption})}",
            "-F", f"file=@{image_path}",
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
        ],
        check=True,
    )


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print(f"Usage: {sys.argv[0]} <channel_id> <image.png> [caption]")
        sys.exit(1)
    channel_id, image_path = sys.argv[1], sys.argv[2]
    caption = sys.argv[3] if len(sys.argv) > 3 else ""
    post(channel_id, image_path, caption)
