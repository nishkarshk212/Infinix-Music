import aiohttp
import asyncio
import ssl

API_URL = "https://youtube-api-saas-backend.onrender.com"
API_KEY = "lily_6ttewJtNQfKvIUUhV6mxKwRwEf0CxJhZ"

async def test_hindi_song():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Known Hindi song video ID: Kesariya from Brahmastra
    video_id = "Vj7nZvn1dgk"
    title = "Kesariya - Brahmastra"
    print(f"Testing Hindi song: {title} (ID: {video_id})")

    # Test downloading this Hindi song via the API
    print("\nTesting download of Hindi song via API...")
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        try:
            async with session.get(
                f"{API_URL}/download",
                params={"id": video_id, "type": "audio"},
                headers={"X-API-Key": API_KEY}
            ) as resp:
                print(f"Status: {resp.status}")
                if resp.status == 200:
                    download_resp = await resp.json()
                    print(f"Download success: {download_resp.get('success')}")
                    print(f"Best audio URL: {download_resp.get('download', {}).get('best_audio_url')}")
                else:
                    print(f"Failed: {await resp.text()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_hindi_song())
