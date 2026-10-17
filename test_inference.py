
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("CRUSOE_API_KEY")

if not api_key:
    raise RuntimeError("CRUSOE_API_KEY missing from .env")

base_url = "https://api.inference.crusoecloud.com/v1"

headers = {"Authorization": f"Bearer {api_key}"}

with httpx.Client(timeout=30) as client:
    models_response = client.get(
        f"{base_url}/models",
        headers=headers
    )
    models_response.raise_for_status()

    models = models_response.json().get("data", [])

    print("Available models:")
    for model in models:
        print("-", model["id"])

    if not models:
        raise RuntimeError("No models returned by Crusoe")

    # Prefer the Qwen model if available.
    qwen_models = [
        m["id"] for m in models
        if "qwen" in m["id"].lower()
    ]

    if not qwen_models:
        raise RuntimeError(
            "No Qwen model found. Select an eligible "
            "open-weight model from the list above."
        )

    model_id = qwen_models[0]
    print("\nTesting:", model_id)

    response = client.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json={
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Suggest three activities "
                        "in San Francisco."
                    )
                }
            ],
            "max_tokens": 250
        }
    )

    response.raise_for_status()
    print("\nModel response:")
    print(
        response.json()["choices"][0]
        ["message"]["content"]
    )
