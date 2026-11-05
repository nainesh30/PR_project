import json
import asyncio
from langchain_openai import ChatOpenAI
from mcp_use import MCPClient
from langchain_ollama.chat_models import ChatOllama

PLANNER_PROMPT = """
You are a STRICT JSON planner.

Allowed tools:
- red_light_on
- red_light_off
- bulb_on
- bulb_off

Rules:
- Output ONLY valid JSON
- Output MUST be a JSON array
- Each element MUST be an object
- Each object MUST have exactly one key: "tool"
- No explanations
- No markdown

Examples:

User: turn on red light
Output:
[
  {"tool": "red_light_on"}
]

User: hello
Output:
[]
"""

def extract_text(resp):
    if isinstance(resp.content, list):
        return "".join(
            part.get("text", "") for part in resp.content if isinstance(part, dict)
        ).strip()
    return str(resp.content).strip()

async def main():
    llm = ChatOllama(
        model='qwen3:4b',
          base_url="http://localhost:11434", 
          reasoning=False    
    
    )

    client = MCPClient.from_config_file("servers.json")

    print("✅ LM Studio Planner + Executor Ready")

    while True:
        try:
            user_input = input("YOU: ").strip()
        except EOFError:
            break

        if not user_input:
            continue

        resp = llm.invoke(PLANNER_PROMPT + "\nUser: " + user_input)
        plan_text = extract_text(resp)

        try:
            plan = json.loads(plan_text)
        except Exception:
            print("❌ Planner output invalid:\n", plan_text)
            continue

        if not plan:
            print("⚠️ No executable actions")
            continue

        for step in plan:
            tool = step["tool"]
            print(f"🔧 Executing: {tool}")
            await client.call_tool(tool, {})

asyncio.run(main())
