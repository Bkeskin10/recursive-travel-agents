
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("CRUSOE_API_KEY")
BASE_URL = "https://api.inference.crusoecloud.com/v1"
MODEL = "Qwen/Qwen3.8-27B"


def ask_llm(system_prompt, user_prompt, max_tokens=1200):
    if not API_KEY:
        raise RuntimeError("CRUSOE_API_KEY is missing")

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "chat_template_kwargs": {
            "enable_thinking": False
        }
    }

    with httpx.Client(timeout=90) as client:
        response = client.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}"
            },
            json=payload
        )

        response.raise_for_status()

        data = response.json()
        message = data["choices"][0]["message"]

        content = message.get("content") or ""
        reasoning = message.get("reasoning_content") or ""

        print("\n=== LLM DEBUG ===")
        print("Finish reason:", data["choices"][0].get("finish_reason"))
        print("Content length:", len(content))
        print("Reasoning length:", len(reasoning))
        print("Usage:", data.get("usage"))
        print("=================\n")

        return content
