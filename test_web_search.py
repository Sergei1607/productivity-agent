import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-haiku-4-5"

response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    tools=[
        {"type": "web_search_20250305", "name": "web_search"}
    ],
    messages=[
        {
            "role": "user",
            "content": "How long does passport renewal currently take for Costa Rican citizens applying from abroad?"
        }
    ],
)

print("stop_reason:", response.stop_reason)
print("---")
for block in response.content:
    print("block type:", block.type)
    print(block)
    print("---")