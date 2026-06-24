import asyncio
import aiohttp
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
API_URL = os.getenv("YOUTUBE_API_URL")
VIDEO_ID = "dQw4w9WgXcQ"  # Test video


async def test_api():
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        ) as session:
            params = {
                "url": f"https://www.youtube.com/watch?v={VIDEO_ID}",
                "type": "audio",
                "api_key": API_KEY
            }
            print(f"Testing API at {API_URL}/download with key {API_KEY[:10]}...")
            async with session.get(
                f"{API_URL}/download",
                params=params
            ) as response:
                print(f"Response status: {response.status}")
                response_json = await response.json()
                print(f"Response: {response_json}")
                if response_json.get("success"):
                    print("API test passed!")
                else:
                    print("API test failed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(test_api())
