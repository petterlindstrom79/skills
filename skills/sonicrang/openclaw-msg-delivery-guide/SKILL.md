---
name: openclaw-msg-delivery-guide
description: Prevent vague follow-up promises in OpenClaw by making message delivery explicit. Use when the user asks how a later result will reach them, how to bind completion to notification, or how to set up scheduled tasks that must notify the user. Choose among cron delivery, subagent completion delivery, background-task follow-up, and `message` + `NO_REPLY`. Default scheduled notifications to OpenClaw cron with `--session isolated` and explicit delivery fields.
metadata:
  openclaw:
    requires:
      bins: ["openclaw"]
      files: ["~/.openclaw/cron/jobs.json"]
      note: "This skill inspects local OpenClaw cron state and may run `openclaw cron` commands or read the persisted cron job file for verification."
---

# OpenClaw Message Delivery Guide

## Problem this skill solves

This skill prevents a common failure mode:

- the agent says "I will send it later"
- background work starts
- no real delivery path is bound
- the user never receives the promised follow-up

Use this skill to make message delivery explicit before promising a later update.

## Local scope disclosure

This skill inspects local OpenClaw scheduler state.
It may:
- run `openclaw cron list`, `openclaw cron run`, `openclaw cron edit`, `openclaw cron enable`, or `openclaw cron disable`
- read `~/.openclaw/cron/jobs.json` to verify persisted cron configuration

Use it when the user wants scheduler or delivery setup, editing, migration, verification, or debugging.

## Core rule

If you say "I will send it when it is done", you must be able to answer these 3 questions clearly:

1. What event counts as completion?
2. Who sends the later message?
3. Which delivery path sends it to the user?

If you cannot answer all 3, the follow-up is not really bound yet.

Do not rely on vague intent like "I will send it later".
Do not assume background work will automatically create a user-visible message.

## Default choice

For anything that is both **scheduled** and **needs notification**, default to:

- **OpenClaw cron**
- **`--session isolated`**
- **explicit delivery**: `--announce --channel <channel> --to <destination>`

Use this default for requests like:
- "Remind me later"
- "Run this every day and notify me"
- "Check this every hour and send me the result"
- "Run this later and notify me"

Do **not** default to these unless the user explicitly asks:
- **Heartbeat**
- **OpenClaw cron `main` session**
- **System cron**

## Minimal cron template

```bash
openclaw cron add \
  --name "Job name" \
  --cron "0 * * * *" \
  --session isolated \
  --message "Do the task. If there is nothing worth reporting, stay silent." \
  --announce \
  --channel <channel> \
  --to <destination>
```

Use the flags on purpose:
- `--session isolated`: avoid main-session delivery ambiguity
- `--announce`: send outward, not just into cron history
- `--channel <channel>`: set the channel explicitly
- `--to <destination>`: set the exact destination explicitly

Useful options:
- `--light-context`: prefer for routine jobs
- `--timeout-seconds <n>`: increase for longer tasks
- `--exact`: use when exact timing matters

Do **not** add `--model` unless the user explicitly asks.

## Binding templates

### 1. Subagent completion

Use when a subagent does the work and the user expects the final result in chat.

Answer the 3 questions like this:
1. **Completion event**: the subagent completion event arrives
2. **Who sends**: the current assistant session
3. **Delivery path**: normal assistant reply in the current chat, or `message(action=send)` if doing a proactive send

Rules:
- `sessions_spawn` only starts the work; it does **not** mean the result has already been sent
- Do not say "I will send it when done" unless you will actually send the completion update when that event arrives
- If a runtime completion event asks for user delivery, rewrite it in your own voice and send it immediately

### 2. Cron notification

Use when the task should run later or repeatedly and notify the user.

Answer the 3 questions like this:
1. **Completion event**: each cron run finishes and produces a reportable result
2. **Who sends**: OpenClaw cron delivery
3. **Delivery path**: `--announce --channel <channel> --to <destination>`

Rules:
- A cron job without delivery fields is not enough if the user expects a visible notification
- If "nothing new" should be silent, say so directly in `--message`
- Prefer `isolated` session unless the user explicitly wants another mode

### 3. `message` + `NO_REPLY`

Use when the visible reply has already been sent through the `message` tool.

Answer the 3 questions like this:
1. **Completion event**: `message(action=send)` succeeds
2. **Who sends**: the `message` tool / channel integration
3. **Delivery path**: the `message` send itself

Rule:
- After a successful `message(action=send)` that already delivered the user-visible content, return only `NO_REPLY`

Do **not** confuse this with future follow-up delivery:
- `NO_REPLY` suppresses duplicate output in the current turn
- it does **not** create a later notification by itself

## Common mistakes

### Background exec/process

Starting a background `exec` or `process` only means the work is running.
It does **not** mean completion will be announced.

If the user expects a later message, add a real follow-up path.

### Vague status promises

Avoid:
- "I will send it later" with no delivery path
- "I will notify you when it is done" when you cannot say who sends it and how
- "I am following up" when nothing user-visible will arrive

Prefer:
- "I have started the background task; there is no final result yet."
- "I have set up a notification every 10 minutes."
- "This message confirms the start; I will send the completion result separately."

## How to fill `channel` and `to`

- If the result should go to the **current chat**, fill `--channel` and `--to` from current session metadata
- If the result should go somewhere else, confirm the destination first
- Do **not** hardcode personal identifiers into this skill

## Test after setup or edit

For periodic jobs, test before relying on the schedule.

Minimum check:
1. confirm the job exists in `openclaw cron list`
2. verify `~/.openclaw/cron/jobs.json`, especially `schedule`, `payload.message`, and delivery fields
3. run `openclaw cron run <job-id>` once
4. confirm the notification actually reached the intended chat

Default closing move:
- ask the user to test once now
