import asyncio
import argparse
from dotenv import load_dotenv

from mcp_use import MCPAgent, MCPClient
from langchain_ollama.chat_models import ChatOllama
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_openai.chat_models import ChatOpenAI


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", default="google", help="lmstudio| ollama | google | openai")
    parser.add_argument("--ollama_model", default="qwen3")
    args = parser.parse_args()

    load_dotenv()

    # ---------- LLM SELECTION ----------
    if args.llm == "lmstudio":
        # LM Studio (OpenAI-compatible)
        llm = ChatOpenAI(
            model="qwen/qwen3-4b-thinking-2507",# name is ignored by LM Studio
            api_key="lm-studio",                  # dummy value
            base_url="http://localhost:1234/v1",  # LM Studio local server
            
        )
    elif args.llm == "ollama":
        llm = ChatOllama(
            model=args.ollama_model,
            base_url="http://localhost:11434",
        )

    elif args.llm == "google":
        llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview"
        )

    elif args.llm == "openai":
        llm = ChatOpenAI(
            model="o4-mini"
        )

    else:
        raise ValueError("Invalid LLM option")

    # ---------- MCP CLIENT ----------
    # client = MCPClient.from_config_file("servers.json")


 

    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # CONFIG_PATH = os.path.join(BASE_DIR, "servers.json")

    # print("📄 Loading MCP config from:", CONFIG_PATH)

    client = MCPClient.from_config_file("servers.json")


    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=2,
        system_prompt=(
                "You are a device control agent.\n"
        "Rules:\n"
        "- Call tools directly\n"
        "- Do NOT explain\n"
        "- Do NOT repeat actions\n"
        "- Do NOT ask questions\n"
        "- After executing tools, STOP\n"
        ),
    )

    print("✅ AI Agent Ready")

    while True:
        try:
            user_input = input("YOU: ")
            if not user_input.strip():
                continue

            result = await agent.run(user_input)
            print("AI:", result)

        except KeyboardInterrupt:
            print("\n👋 Exiting agent")
            break


if __name__ == "__main__":
    asyncio.run(main())
