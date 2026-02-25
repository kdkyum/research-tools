---
name: submit-report
description: >
  Submit a research report to the Research Dashboard. Use this skill whenever
  the user wants to submit, upload, or push a report to the dashboard, or after
  generating a research report and the user says "submit it", "upload to
  dashboard", "push this report", "send to dashboard", or "submit report".
  Also triggers on: "update the report on the dashboard", "resubmit",
  "sync report to dashboard". Even if the user just says "submit" after
  running /research-report, use this skill. Works with any markdown report
  in research_notes/ — auto-detects the latest one if no file is specified.
---

# Submit Report to Research Dashboard

Submit a markdown research report (and its figures) to the centralized
Research Dashboard. The dashboard collects reports from multiple servers
and provides a searchable, browsable web UI.

## Prerequisites

The submit script lives at a known location on the dashboard server.
Set these environment variables (or pass as flags):

- `DASHBOARD_URL` — The dashboard server URL (e.g. `https://89.168.72.192:3000`)
- `DASHBOARD_API_KEY` — API key for write access

If the env vars aren't set, check `~/.dashboard.env` or ask the user.

The submit script is at: `/home/ubuntu/Projects/report_dashboard/scripts/submit-report.sh`

## Arguments

- `$ARGUMENTS` may contain:
  - A specific report file path
  - `--update` flag to update an existing report
  - `--project NAME` to set the project
  - `--tags tag1,tag2` to set tags
  - Any other flags supported by submit-report.sh

## Workflow

### 1. Identify the report to submit

If `$ARGUMENTS` contains a file path, use that. Otherwise, find the most
recent `.md` file in `research_notes/`:

```bash
ls -t research_notes/*.md | head -1
```

Read the report to understand its content — you'll need the title, project
context, and what it's about to fill in metadata.

### 2. Determine project name and tags

Try to infer these automatically:

- **Project**: Check if there's a pattern in the directory name, git remote
  URL, or report content. Common patterns: the git repo name, or the parent
  directory name. If uncertain, ask the user.
- **Tags**: Extract from the report content — look for keywords like model
  names, techniques (ablation, finetuning, scaling), dataset names, or
  key metrics. Pick 2-5 relevant tags.

If the user provided `--project` or `--tags` in `$ARGUMENTS`, use those
instead of inferring.

### 3. Check for update mode

If `--update` is in `$ARGUMENTS`, or if the user says "resubmit" or
"update the report", add the `--update` flag. This tells the dashboard
to find the existing report by title+project and create a new version
rather than a duplicate.

### 4. Submit via the script

Run the submit script with all collected parameters:

```bash
/home/ubuntu/Projects/report_dashboard/scripts/submit-report.sh \
  <report_file> \
  --server "${DASHBOARD_URL}" \
  --api-key "${DASHBOARD_API_KEY}" \
  --project "<project_name>" \
  --tags "<tag1,tag2,tag3>" \
  --user "$(hostname)-claude" \
  [--update]
```

The script automatically:
- Collects environment info (hostname, Python version, GPU, CUDA)
- Collects git info (branch, commit, remote, dirty status)
- Auto-detects attachments from `research_notes/attachements/` that
  match the report's notebook prefix
- Uploads everything as a multipart POST to the dashboard API
- Handles deduplication (returns 409 if duplicate, use `--force` to override)
- In update mode, finds existing report by title and creates a new version

### 5. Report the result

After submission, tell the user:
- Whether the submission succeeded or failed
- The report ID and dashboard URL for viewing
- If it was an update, mention the version number
- If it was a duplicate, suggest using `--update` or `--force`

## Environment variable loading

Before running the script, source credentials if they exist:

```bash
# Check for dashboard env file
if [ -f ~/.dashboard.env ]; then
  source ~/.dashboard.env
fi
```

If neither env vars nor the file exist, tell the user they need to set
`DASHBOARD_URL` and `DASHBOARD_API_KEY`. Point them to the dashboard
admin for API key provisioning.

## Example flows

**Simple submit after writing a report:**
```
User: "submit this report to the dashboard"
→ Find latest report in research_notes/
→ Infer project from git repo name
→ Extract tags from report content
→ Run submit-report.sh
→ Report success with dashboard URL
```

**Update an existing report:**
```
User: "I updated the report, resubmit it"
→ Find the report file
→ Run submit-report.sh with --update
→ Dashboard creates a new version
→ Report version number and URL
```

**Explicit project and tags:**
```
User: "/submit-report research_notes/2025-01-15_ablation.md --project transformer-scaling --tags ablation,attention"
→ Use the specified file, project, and tags directly
→ Run submit-report.sh
→ Report success
```

## Troubleshooting

- **409 Conflict**: Report already exists. Use `--update` to version it,
  or `--force` to submit as a new report anyway.
- **Connection refused**: Check that the dashboard server is running and
  the URL is correct. The server uses HTTPS with a self-signed cert,
  so curl needs `-k` (the script already handles this).
- **401 Unauthorized**: API key is wrong or missing. Check `DASHBOARD_API_KEY`.
- **No attachments detected**: The script looks for files in
  `research_notes/attachements/` matching the notebook prefix from the
  report's frontmatter. If the report doesn't reference a notebook,
  all images in the attachements folder are included.
