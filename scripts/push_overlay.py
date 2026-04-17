from __future__ import annotations

import argparse
import json
import urllib.request


def main() -> None:
    parser = argparse.ArgumentParser(description="Push a rendered line to the desktop overlay.")
    parser.add_argument("--reply", required=True)
    parser.add_argument("--message", default="")
    parser.add_argument("--preset", default=None)
    parser.add_argument("--url", default="http://127.0.0.1:44777/v1/display")
    args = parser.parse_args()

    payload = {
        "message": args.message,
        "reply": args.reply,
        "preset_id": args.preset,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        args.url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        print(response.read().decode("utf-8"))


if __name__ == "__main__":
    main()
