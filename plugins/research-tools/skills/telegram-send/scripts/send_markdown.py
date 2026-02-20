#!/usr/bin/env python3
"""Send a markdown file to Telegram chat.

Usage:
    python send_markdown.py <file_path> [--config ~/.telegram_notify.conf] [--as-document]

Reads T_TOKEN and CHAT_ID from the config file.
By default, sends as formatted text messages (splitting at 4096 char limit).
With --as-document, sends the file as-is as a document attachment.
"""
import argparse
import os
import re
import sys
import urllib.error
import urllib.parse
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


def escape_markdownv2(text):
    """Escape special characters for Telegram MarkdownV2, preserving bold/italic/code."""
    # Characters that must be escaped in MarkdownV2
    # (outside of code blocks and inline code)
    special = r"_[]()~`>#+=|{}.!-"
    # We'll do a simpler approach: send as HTML instead, which is easier to
    # convert from markdown.
    return text


def markdown_to_html(text):
    """Minimal markdown-to-HTML conversion for Telegram's supported HTML subset.

    Telegram supports: <b>, <i>, <code>, <pre>, <a href="">, <u>, <s>
    """
    lines = text.split("\n")
    out = []
    in_code_block = False

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                out.append("</pre>")
                in_code_block = False
            else:
                lang = line.strip()[3:].strip()
                out.append("<pre>")
                in_code_block = True
            continue

        if in_code_block:
            out.append(html_escape(line))
            continue

        # Headers -> bold
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            out.append(f"\n<b>{html_escape(m.group(2))}</b>\n")
            continue

        # Horizontal rules
        if re.match(r"^(-{3,}|\*{3,}|_{3,})\s*$", line):
            out.append("---")
            continue

        # Process inline formatting
        processed = process_inline(line)
        out.append(processed)

    if in_code_block:
        out.append("</pre>")

    return "\n".join(out)


def html_escape(text):
    """Escape HTML special chars."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def process_inline(line):
    """Process inline markdown: bold, italic, code, links, images."""
    # First escape HTML
    line = html_escape(line)

    # Inline code (before other formatting)
    line = re.sub(r"`([^`]+)`", r"<code>\1</code>", line)

    # Bold: **text** or __text__
    line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
    line = re.sub(r"__(.+?)__", r"<b>\1</b>", line)

    # Italic: *text* or _text_  (but not inside words with underscores)
    line = re.sub(r"(?<!\w)\*([^*]+?)\*(?!\w)", r"<i>\1</i>", line)

    # Images: ![alt](url) -> just the alt text
    line = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"[\1]", line)

    # Links: [text](url)
    line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', line)

    # LaTeX: $...$ -> code (best approximation)
    line = re.sub(r"\$\$(.+?)\$\$", r"<code>\1</code>", line)
    line = re.sub(r"\$(.+?)\$", r"<code>\1</code>", line)

    return line


def split_message(text, limit=4096):
    """Split text into chunks that fit Telegram's message size limit.

    Splits on paragraph boundaries (double newline) when possible.
    """
    if len(text) <= limit:
        return [text]

    chunks = []
    current = ""

    paragraphs = text.split("\n\n")
    for para in paragraphs:
        candidate = current + ("\n\n" if current else "") + para
        if len(candidate) <= limit:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # If a single paragraph exceeds the limit, split on newlines
            if len(para) > limit:
                lines = para.split("\n")
                current = ""
                for line in lines:
                    candidate = current + ("\n" if current else "") + line
                    if len(candidate) <= limit:
                        current = candidate
                    else:
                        if current:
                            chunks.append(current)
                        # If a single line exceeds limit, hard-split
                        while len(line) > limit:
                            chunks.append(line[:limit])
                            line = line[limit:]
                        current = line
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


def send_message(token, chat_id, text, parse_mode="HTML"):
    """Send a text message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        if not result.get("ok"):
            print(f"Telegram API error: {result}", file=sys.stderr)
            return False
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        # If HTML parse fails, retry as plain text
        if parse_mode == "HTML" and "can't parse entities" in body.lower():
            print("Retrying as plain text...", file=sys.stderr)
            return send_message(token, chat_id, text, parse_mode=None)
        return False


def send_document(token, chat_id, file_path):
    """Send a file as a document attachment via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendDocument"

    boundary = "----PythonFormBoundary"
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
        f"{chat_id}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'
        f"Content-Type: text/markdown\r\n\r\n"
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
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Send markdown file to Telegram")
    parser.add_argument("file", help="Path to the markdown file")
    parser.add_argument("--config", default="~/.telegram_notify.conf",
                        help="Path to config file (default: ~/.telegram_notify.conf)")
    parser.add_argument("--as-document", action="store_true",
                        help="Send as document attachment instead of formatted text")
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

    if args.as_document:
        print(f"Sending {file_path} as document...")
        ok = send_document(token, chat_id, file_path)
        if ok:
            print("Document sent.")
        else:
            sys.exit(1)
    else:
        with open(file_path) as f:
            md_text = f.read()

        html = markdown_to_html(md_text)
        chunks = split_message(html)
        total = len(chunks)
        print(f"Sending {file_path} as {total} message(s)...")

        for i, chunk in enumerate(chunks, 1):
            ok = send_message(token, chat_id, chunk)
            if ok:
                print(f"  [{i}/{total}] sent")
            else:
                print(f"  [{i}/{total}] FAILED", file=sys.stderr)
                sys.exit(1)

        print("Done.")


if __name__ == "__main__":
    main()
