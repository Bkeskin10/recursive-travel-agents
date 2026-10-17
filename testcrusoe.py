
import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("CRUSOE_API_KEY")
BASE_URL = "https://api.inference.crusoecloud.com/v1"

async def main():
    if not API_KEY:
        print("ERROR: CRUSOE_API_KEY missing from .env")
        return

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
            f"{BASE_URL}/models",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )

        response.raise_for_status()
        models = response.json()

        print("Connected to Crusoe!")
        print(models)

if __name__ == "__main__":
    asyncio.run(main())
