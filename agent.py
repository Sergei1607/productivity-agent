import os
import json
import requests
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

MODEL = "claude-haiku-4-5"


def read_tasks():
    with open("tasks.json", "r") as f:
        return json.load(f)


def send_briefing_email(subject, body):
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": "onboarding@resend.dev",
            "to": "sergei.redondo@gmail.com",
            "subject": subject,
            "text": body,
        },
    )
    return {"status_code": response.status_code, "response": response.json()}


TOOLS = [
    {
        "name": "read_tasks",
        "description": "Read the current list of tasks, each with an id, title, and free-text notes.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "type": "web_search_20250305",
        "name": "web_search",
    },
    {
        "name": "send_briefing_email",
        "description": "Send the finished daily briefing as an email. Call this exactly once, after composing the full briefing text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "The email subject line."
                },
                "body": {
                    "type": "string",
                    "description": "The full plain-text briefing to send as the email body. No markdown, no bullet points, no emoji."
                },
            },
            "required": ["subject", "body"],
        },
    },
]


def run_tool(name, tool_input):
    if name == "read_tasks":
        return read_tasks()
    elif name == "send_briefing_email":
        return send_briefing_email(tool_input["subject"], tool_input["body"])
    else:
        raise ValueError(f"Unknown tool: {name}")


SYSTEM_PROMPT = """You are a personal productivity assistant. Each run, you:

1. Call read_tasks to see the current list of tasks.
2. For any task whose notes suggest a real question that a quick web search could help answer (a deadline, a requirement, a fact you're unsure of), call web_search to look it up. Do not search for every task - only ones where a lookup would genuinely help.
3. 3. Compose a short, friendly "here's your day" briefing in plain text. No markdown, no bullet points, no bold, no emoji, no citation tags or source markers of any kind (e.g. no <cite> tags, no footnote numbers, no bracketed references). Blend anything you found from web searches directly into the sentence as plain prose, the way you'd casually mention something you happened to know. Mention each task briefly.ul you found from web searches.
4. Call send_briefing_email exactly once with a subject line and the briefing as the body. Do not call it more than once.

Keep the briefing concise - a few short paragraphs, not an exhaustive report."""


def main():
    messages = [
        {"role": "user", "content": "Give me my daily briefing."}
    ]

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    main()