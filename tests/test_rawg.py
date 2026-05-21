import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAWG_API_KEY")
RAWG_BASE_URL = "https://api.rawg.io/api"


async def get_games(api_key=API_KEY):
    if not API_KEY:
        raise RuntimeError("Brak API KEY")

    async with httpx.AsyncClient(base_url=RAWG_BASE_URL) as client:
        response = await client.get("/games", params={"key": api_key})
        response.raise_for_status()
        return response.json()


async def main():
    data = await get_games()
    print(data["count"])  # 899298
    # for game in data['results']:
    #    print(game['name'], game['rating'])


if __name__ == "__main__":
    asyncio.run(main())
