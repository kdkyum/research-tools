---
name: send-telegram
description: Send a file to Telegram chat. Usage: /send-telegram <file_path> [--as-document]
user_invocable: true
---

Send the specified file to the user's Telegram chat using the telegram-send skill.

Arguments:
- `$ARGUMENTS` contains the file path and optional flags

Steps:
1. Parse the file path from `$ARGUMENTS`
2. Run the send script:

```bash
python <skill-dir-for:telegram-send>/scripts/send_markdown.py <file_path> [flags]
```

If `$ARGUMENTS` is empty, look for the most recent file in `research_notes/` and offer to send it.
