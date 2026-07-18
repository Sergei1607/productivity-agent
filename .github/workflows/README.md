# Personal Productivity Agent

A daily "here's your day" briefing agent, built on the Claude API with tool use. Extends Project 5A (Inbox/Task Triage Agent) from a 2-tool loop into a 3-tool agent that mixes client-side and Anthropic-hosted tools in the same conversation.

## What it does

Each morning, the agent:
1. Reads the current task list.
2. Judges, per task, whether a quick web search would add something useful (a deadline, a requirement, a fact worth checking) — not every task, only ones where it genuinely helps.
3. Composes a short, plain-text daily briefing weaving in anything useful it found.
4. Emails the briefing.

Runs automatically every day at 8:00 AM Costa Rica time via a scheduled GitHub Action, with a manual trigger available for testing.

## Tech stack

- Python
- Anthropic Claude API (model: `claude-haiku-4-5`), using both a client-defined tool and an Anthropic-hosted server tool in the same agent loop
- Resend API for email delivery
- GitHub Actions for scheduling

## Tools

- `read_tasks` (client tool) — reads task data from a local `tasks.json`
- `web_search` (Anthropic-hosted tool) — Anthropic's servers execute the search and return results directly to Claude within the same API call; no client-side execution code needed
- `send_briefing_email` (client tool) — sends the finished briefing via the Resend REST API

## A note on hosted vs. client tools

This project deliberately mixes both tool types to make the distinction concrete rather than theoretical. Client tools (`read_tasks`, `send_briefing_email`) are fully defined and executed locally — the agent loop watches for `stop_reason == "tool_use"` and dispatches accordingly. `web_search` is hosted: it's declared in the `tools` list with no schema or execution code, Anthropic's servers run it, and the agent loop never sees a pending request for it at all. Verified this directly during development — a response using only `web_search` returned `stop_reason: "end_turn"`, not `"tool_use"`.

## Known limitations

- Uses a static local `tasks.json` rather than the live note-app API (same deliberate scoping choice as Project 5A, to isolate this project's new concepts from Render's free-tier cold-start flakiness)
- No calendar integration — deferred as a stretch goal, since Google Calendar's OAuth model is a meaningfully different, fussier auth pattern than the API-key auth used everywhere else in this project
- Resend account runs in sandbox mode (no verified custom domain), so email can currently only be sent *from* `onboarding@resend.dev` *to* the account owner's own registered address — not yet suitable for briefing anyone but the account owner

## What's next

- Verify a custom sending domain in Resend to remove the single-recipient restriction
- Swap the local `tasks.json` for the real note-app API
- Add Google Calendar as a fourth tool, as a dedicated follow-up focused on OAuth

## Setup

Requires a `.env` file (gitignored) with `ANTHROPIC_API_KEY` and `RESEND_API_KEY`. For local runs: