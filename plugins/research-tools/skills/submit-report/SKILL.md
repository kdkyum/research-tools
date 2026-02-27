---
name: submit-report
description: >
  Submit a research report to the Research Dashboard. Use this skill whenever
  the user wants to submit, upload, or push a report to the dashboard, or after
  generating a research report and the user says "submit it", "upload to
  dashboard", "push this report", "send to dashboard", or "submit report".
  Also triggers on: "resubmit", "sync report to dashboard".
  Even if the user just says "submit" after
  running /research-report, use this skill. Works with any markdown report
  in research_notes/ — auto-detects the latest one if no file is specified.
---

# Submit Report to Research Dashboard

Submit a markdown research report (and its figures) to the centralized
Research Dashboard via its REST API. No external scripts needed — just
curl. Works from any server.

## Credentials

Read from environment or `~/.dashboard.env`:

```bash
if [ -f ~/.dashboard.env ]; then source ~/.dashboard.env; fi
```

Required variables:
- `DASHBOARD_URL` — e.g. `https://89.168.72.192:3000`
- `DASHBOARD_API_KEY` — API key for write access

Optional:
- `DASHBOARD_USER` — Fixed user/instance name (e.g. `gpu-cluster-claude`).
  If not set, falls back to `$(hostname)-claude`. Useful when running on
  SLURM compute nodes where hostname changes per job — set this to the
  login node name so all reports from the same cluster appear under one user.

If missing, tell the user to create `~/.dashboard.env` with both values.

## Arguments

`$ARGUMENTS` may contain:
- A report file path
- `--project NAME` to set the project name
- `--tags tag1,tag2` to set tags
- `--force` to skip duplicate check

## Workflow

### 1. Find the report

If a file path is in `$ARGUMENTS`, use it. Otherwise find the latest:

```bash
ls -t research_notes/*.md | head -1
```

Read the report to extract its title (first `# ` heading or `title:` in
frontmatter) and understand the content for tag inference.

### 2. Infer project and tags

- **Project**: Use git repo name (`basename $(git remote get-url origin .git)`)
  or the current directory name. Use explicit `--project` if provided.
- **Tags**: Pick 2-5 from the report content — model names, techniques
  (ablation, finetuning, scaling), dataset names. Use explicit `--tags`
  if provided.

### 3. Collect attachments

Find figures in `research_notes/attachements/` that belong to this report.
If the report references a notebook (e.g. `notebooks/foo.ipynb`), only
include files matching `foo_*`. Otherwise include all image files:

```bash
# All images in attachements/
ls research_notes/attachements/*.{png,jpg,svg,pdf} 2>/dev/null
```

### 4. Submit via curl

Build a multipart request with all the data:

```bash
# Collect environment info
HOSTNAME=$(hostname)
PY_VER=$(python3 --version 2>&1 | awk '{print $2}' || echo "")
GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 || echo "")
ENV_JSON="{\"hostname\":\"${HOSTNAME}\",\"pythonVersion\":\"${PY_VER}\"}"
# Add GPU if available
if [ -n "$GPU" ]; then
  CUDA_VER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1 || echo "")
  ENV_JSON="{\"hostname\":\"${HOSTNAME}\",\"pythonVersion\":\"${PY_VER}\",\"gpu\":\"${GPU}\",\"cudaVersion\":\"${CUDA_VER}\"}"
fi

# Collect git info
GIT_JSON="{}"
if git rev-parse --is-inside-work-tree &>/dev/null; then
  GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
  GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "")
  GIT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
  GIT_DIRTY=$(git diff --quiet 2>/dev/null && echo "false" || echo "true")
  GIT_JSON="{\"branch\":\"${GIT_BRANCH}\",\"commit\":\"${GIT_COMMIT}\",\"remoteUrl\":\"${GIT_REMOTE}\",\"dirty\":${GIT_DIRTY}}"
fi

# Build curl command
curl -sk \
  -X POST "${DASHBOARD_URL}/api/reports" \
  -H "X-API-Key: ${DASHBOARD_API_KEY}" \
  -F "report=@research_notes/<report_file>" \
  -F "project=${PROJECT}" \
  -F "user=${DASHBOARD_USER:-$(hostname)-claude}" \
  -F "tags=${TAGS}" \
  -F "env=${ENV_JSON}" \
  -F "git=${GIT_JSON}" \
  -F "force=false" \
  -F "attachment=@research_notes/attachements/fig1.png" \
  -F "attachment=@research_notes/attachements/fig2.png"
```

Use `-sk` because the dashboard uses a self-signed TLS certificate.
Repeat `-F "attachment=@..."` for each figure file.

### 5. Handle the response

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 201 | Created | Report success, show dashboard URL |
| 409 | Duplicate | Suggest `--force` to override |
| 401 | Bad API key | Check `DASHBOARD_API_KEY` |
| 413 | Too large | Reduce attachment size |

On success, extract the report ID from the JSON response and show:
```
View at: ${DASHBOARD_URL}/#/report/<id>
```

## Example flows

**Simple submit:**
```
User: "submit this to the dashboard"
→ Find latest .md in research_notes/
→ Infer project from git repo name
→ Extract 3 tags from content
→ Collect matching figures from attachements/
→ POST to dashboard API
→ "Submitted! View at https://89.168.72.192:3000/#/report/2025-..."
```

**Resubmit after edits:**
```
User: "I updated the report, resubmit"
→ Find the report
→ POST with --force to skip duplicate check
→ "Submitted! View at ..."
```
