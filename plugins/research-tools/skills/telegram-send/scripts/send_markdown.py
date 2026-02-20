#!/usr/bin/env python3
"""Send a file to Telegram chat as a document.

Usage:
    python send_markdown.py <file_path> [--config ~/.telegram_notify.conf]

Reads T_TOKEN and CHAT_ID from the config file.
Always sends as a document attachment (HTML, markdown, or any file).
"""
import argparse
import os
import sys
import urllib.error
import urllib.request
import json


def load_config(config_path):
    """Parse shell-style KEY=VALUE config file."""
    config = {}
    path = os.path.expanduser(config_path)
    if not os.path.exists(path):
        print(f"Error: config file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                config[key.strip()] = val.strip().strip('"').strip("'")
    return config


MIME_TYPES = {
    ".html": "text/html",
    ".htm": "text/html",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".csv": "text/csv",
    ".json": "application/json",
}


def send_document(token, chat_id, file_path):
    """Send a file as a document attachment via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendDocument"

    boundary = "----PythonFormBoundary"
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    mime = MIME_TYPES.get(ext, "application/octet-stream")

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
        f"{chat_id}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        if not result.get("ok"):
            print(f"Telegram API error: {result}", file=sys.stderr)
            return False
        return True
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {err_body}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Send a file to Telegram")
    parser.add_argument("file", help="Path to the file to send")
    parser.add_argument("--config", default="~/.telegram_notify.conf",
                        help="Path to config file (default: ~/.telegram_notify.conf)")
    args = parser.parse_args()

    file_path = os.path.expanduser(args.file)
    if not os.path.exists(file_path):
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    token = config.get("T_TOKEN")
    chat_id = config.get("CHAT_ID")
    if not token or not chat_id:
        print("Error: T_TOKEN and CHAT_ID must be set in config", file=sys.stderr)
        sys.exit(1)

    print(f"Sending {file_path} as document...")
    ok = send_document(token, chat_id, file_path)
    if ok:
        print("Document sent.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
