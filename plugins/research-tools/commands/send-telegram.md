---
name: send-telegram
description: Send a file to Telegram chat. Usage: /send-telegram <file_path>
user_invocable: true
---

Send the specified file to the user's Telegram chat as a document attachment.

Arguments:
- `$ARGUMENTS` contains the file path

Steps:
1. Parse the file path from `$ARGUMENTS`
2. Run the send script:

```bash
python <skill-dir-for:telegram-send>/scripts/send_markdown.py <file_path>
```

If `$ARGUMENTS` is empty, look for the most recent `.html` file in `research_notes/` and offer to send it. If no HTML exists, suggest building one first with `.venv/bin/python scripts/build_research_html.py`.
