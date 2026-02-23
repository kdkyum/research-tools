---
name: send-telegram
description: Send a file to Telegram chat. Usage: /send-telegram <file_path> [--no-document]
user_invocable: true
---

Send the specified file to the user's Telegram chat using the telegram-send skill.

Arguments:
- `$ARGUMENTS` contains the file path and optional flags

Steps:
1. Parse the file path from `$ARGUMENTS`
2. If the file is a markdown report from `research_notes/`, first build HTML:

```bash
.venv/bin/python <skill-dir-for:telegram-send>/scripts/build_research_html.py \
    --notes-dir research_notes \
    --out /tmp/research_report.html
```

Then send the HTML:

```bash
python <skill-dir-for:telegram-send>/scripts/send_markdown.py /tmp/research_report.html
```

3. For other files, send directly as a document:

```bash
python <skill-dir-for:telegram-send>/scripts/send_markdown.py <file_path>
```

If `$ARGUMENTS` is empty, look for the most recent file in `research_notes/` and offer to build HTML and send it.
