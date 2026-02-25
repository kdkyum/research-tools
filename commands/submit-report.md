---
name: submit-report
description: Submit a research report to the dashboard. Usage: /submit-report [file] [--update] [--project NAME] [--tags t1,t2]
user_invocable: true
---

Submit the specified (or latest) research report to the Research Dashboard using the submit-report skill.

Arguments:
- `$ARGUMENTS` contains the optional file path and flags

Steps:
1. Parse `$ARGUMENTS` for file path and flags (--update, --project, --tags)
2. If no file specified, find the latest report in `research_notes/`
3. Source `~/.dashboard.env` if it exists for DASHBOARD_URL and DASHBOARD_API_KEY
4. Infer project name and tags from report content if not provided
5. Collect figures from `research_notes/attachements/`
6. Submit via curl multipart POST to `${DASHBOARD_URL}/api/reports`
7. Report the result — success URL or error with guidance

If `$ARGUMENTS` is empty, auto-detect the latest report and confirm with the user before submitting.
