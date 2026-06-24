import os
import re
import aiohttp
import ssl
from dataclasses import dataclass

# Copy of Track dataclass
@dataclass
class Track:
    id: str
    channel_name: str
    duration: str
    duration_sec: int
    title: str
    url: str
    file_path: str = None
    message_id: int = 0
    time: int = 0
    thumbnail: str = None
    user: str = None
    view_count: str = None
    video: bool = False

# Copy of YouTube class
API_URL = "https://youtube-api-music.onrender.com"
DOWNLOAD_DIR = "downloads"

class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        self.cookie_dir = "Infinix/cookies"

    async def download(self, video_id: str, video: bool = False, api_key: str = None) -> str | None:
        if not video_id or len(video_id) < 3:
            return None

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        ext = "mkv" if video else "webm"
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

        if os.path.exists(file_path):
            return file_path

        try:
            # Create ssl context that doesn't check certs to avoid errors with render
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=ssl_context)
            ) as session:
                params = {
                    "id": video_id,
                    "type": "video" if video else "audio"
                }
                headers = {
                    "X-API-Key": api_key
                }

                async with session.get(
                    f"{API_URL}/download",
                    params=params,
                    headers=headers
                ) as resp:
                    print(f"Download endpoint status: {resp.status}")
                    if resp.status == 401:
                        print("Invalid API key")
                        return None
                    if resp.status != 200:
                        text = await resp.text()
                        print(f"Error: {text}")
                        return None

                    response_json = await resp.json()
                    if not response_json.get("success"):
                        print(f"Success flag false: {response_json}")
                        return None

                    data = response_json.get("download", {})
                    # Get appropriate URL
                    if video:
                        download_link = data.get("best_video_url") or data.get("best_audio_url")
                    else:
                        download_link = data.get("best_audio_url") or data.get("best_video_url")

                    if not download_link:
                        print(f"No download link found: {response_json}")
                        return None
                    print(f"Downloading from: {download_link}")

                # Now download from the obtained link
                async with session.get(download_link, ssl=ssl_context) as file_response:
                    if file_response.status != 200:
                        print(f"File download failed ({file_response.status})")
                        return None
                    with open(file_path, "wb") as f:
                        async for chunk in file_response.content.iter_chunked(8192):
                            f.write(chunk)

            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return file_path
        except Exception as e:
            print(f"Download exception: {e}")
            import traceback
            print(traceback.format_exc())
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
        return None

# Test script
API_KEY = "tcRkjxRJ5aB59r5thtYLFWiGLlOfCgN1z8zNJupEDI8"

async def test_hindi_song_download():
    yt = YouTube()
    
    # First test with known working video ID
    print("First, testing with known working video ID (dQw4w9WgXcQ)...")
    test_video_id = "dQw4w9WgXcQ"
    file_path = await yt.download(test_video_id, video=False, api_key=API_KEY)
    if file_path:
        print(f"✓ Known video works! Downloaded to: {file_path} (size: {os.path.getsize(file_path)} bytes)")
    else:
        print("✗ Known video failed, something's wrong!")
        return
    
    # Now let's test with a valid Hindi song. Let's find a valid Hindi song video ID!
    # Let's try "Kalank - Title Track" - video ID "e0S9QdD23hE"
    print("\nTesting with Hindi song (Kalank - Title Track, ID: e0S9QdD23hE)...")
    hindi_video_id = "e0S9QdD23hE"
    file_path = await yt.download(hindi_video_id, video=False, api_key=API_KEY)
    if file_path:
        print(f"✓ Hindi song works! Downloaded to: {file_path} (size: {os.path.getsize(file_path)} bytes)")
    else:
        print("✗ Hindi song video ID failed, let's try another one (Channa Mereya - ID: fN4x7O79nwo)...")
        hindi_video_id = "fN4x7O79nwo"
        file_path = await yt.download(hindi_video_id, video=False, api_key=API_KEY)
        if file_path:
            print(f"✓ Hindi song works! Downloaded to: {file_path} (size: {os.path.getsize(file_path)} bytes)")
        else:
            print("Let's try one more (Ae Dil Hai Mushkil - ID: kJQP7kiw5Fk)...")
            hindi_video_id = "kJQP7kiw5Fk"
            file_path = await yt.download(hindi_video_id, video=False, api_key=API_KEY)
            if file_path:
                print(f"✓ Hindi song works! Downloaded to: {file_path} (size: {os.path.getsize(file_path)} bytes)")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_hindi_song_download())
