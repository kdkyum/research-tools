---
name: recall
description: "Reconstruct recent working context from Claude Code transcripts, current repository state, and linked GitHub history. Use for 'recall my work on X', 'catch me up', 'what have I been working on', 'where did I leave off', or before resuming work."
disable-model-invocation: true
---

# Recall

Rebuild the user's recent working context before starting or resuming work. Read
only the relevant sessions. Return a short brief that says what changed, what
remains open, and what to do next.

Keep raw transcript content out of the main conversation when several sessions
need review. Assign the reading to subagents and keep only their findings.

## Where Claude Code stores transcripts

Claude Code stores project history under `~/.claude/projects/`.

```
~/.claude/projects/<project-slug>/
├── sessions-index.json
├── <session-id>.jsonl
└── <session-id>/
    └── subagents/
        └── agent-<id>.jsonl
```

A top-level `<session-id>.jsonl` file contains one session. The
`sessions-index.json` file maps each session to its original `projectPath` and
records its first prompt, summary, timestamps, branch, and sidechain status.
Subagent transcripts live below the session directory and are not primary
sessions.

Find the directory by matching the active workspace from `pwd -P` against the
`projectPath` fields in `~/.claude/projects/*/sessions-index.json`. This is more
reliable than guessing the directory name. If no index matches, replace each
slash in the absolute workspace path with a hyphen. The leading slash becomes
the first hyphen. For example, `/Users/you/proj` usually maps to
`~/.claude/projects/-Users-you-proj/`.

## Workflow

### 1. Set the scope

Identify three things before searching:

- The time window. Use the last seven days when the user says "recent".
- The topic. Use the named feature, file, bug, branch, or question.
- The workspace. Use the active workspace unless the user names another one.

State the scope. Never search another project's transcripts without the user's
request. If the user supplies a complete state summary with paths, branch, and
next step, use it instead of mining transcripts.

If the user names one session ID, read that session directly. Broad recall is
for rebuilding context across several sessions.

### 2. Find candidate sessions

Use `sessions-index.json` to shortlist sessions by `modified`, `firstPrompt`,
`summary`, `gitBranch`, and `isSidechain`. Then confirm recency with the real
modification time of each `.jsonl` file. Sort by file modification time, not by
session ID.

Search only top-level `.jsonl` files. Skip these records:

- The current session, whose ID is in `CLAUDE_CODE_SESSION_ID` when that
  variable is available.
- Entries where `isSidechain` is `true`.
- Subagent transcripts under `<session-id>/subagents/`.
- Sessions outside the chosen time window.
- Eval and test sessions unless the topic requires them.

Search the topic in the short list before reading full transcripts. Use `rg`
for the first pass. Read only the matching regions and enough surrounding lines
to understand the decision or result.

### 3. Read the relevant sessions

For one or two candidates, read them directly. For three or more candidates,
assign slices to parallel subagents. A cheap model is enough for transcript
search. Give every subagent the same rules:

- Process sessions in modification-time order.
- Search for the topic before reading.
- Read only relevant regions unless the answer depends on the agent's exact
  sequence of tool calls or errors.
- Do not copy private transcript text into the report.
- Return one block per session with the schema below.

```text
Session: <session-id>
Topic: <short label>
User goal: <what the user wanted>
Decisions: <decisions and reasons>
Current state: <what was completed or left in progress>
Problems: <errors, failed attempts, corrections, or reversions>
Artifacts: <files, branches, commits, PRs, issues, and URLs>
Next step: <the unfinished action, if any>
```

Cite each finding with its session ID. Keep raw transcripts in the subagents.

### 4. Check the shared record

When the topic names a feature, file, subsystem, or bug, search the record
outside the transcripts. Start with the sources available in the current
environment:

- Git history, branches, tags, and working-tree state
- GitHub pull requests and issues through `gh`
- Project documentation and changelogs
- Connected issue trackers, chat systems, or error trackers when available

If a `why` skill is installed, use it for this search. Otherwise, search the
available sources directly. Do not treat an unavailable integration as an
error. State which source was unavailable.

Ask what is true now, what was tried and reverted, and what users still report.
Skip this step for a pure activity question such as "what did I do this week"
when no feature or bug is named.

### 5. Verify the live state

A transcript records history, not current truth. Check every surfaced branch,
commit, pull request, issue, and changed file with `git`, `gh`, or the relevant
system. If the answer depends on the tools an agent ran or an error it saw, read
the full transcript instead of relying on its summary.

### 6. Write the brief

Apply the `unslop` skill. Group the brief by work thread and keep unrelated work
out. Sanitize private context before placing it in any public document, issue,
or pull request.

## Output contract

Write the sections below in this order.

- **Capsule.** At most five bullets. State what the work is and where it stands.
- **Threads.** Give each thread one line and one status tag. Use `[merged #N]`,
  `[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`,
  `[reverted #N]`, or `[planned, not started]`.
- **Problems.** List at most five recurring problems. Include user symptoms and
  fixes that shipped and were reverted.
- **Next move.** Name the single most useful next action.

Cite transcript findings by session ID. Cite shared-record findings by pull
request number, issue ID, commit, document path, or external URL.

**Reply:** Return only the brief.
