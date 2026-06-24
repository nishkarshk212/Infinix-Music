
import os
import re
import aiohttp
import random
import ssl
import asyncio
from py_yt import VideosSearch, Playlist
from Infinix import logger, config, db
from Infinix.helpers import Track, utils

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
        self.download_queue = asyncio.Queue()  # Background download queue
        self.download_task = None

    def get_cookies(self):
        if not os.path.exists(self.cookie_dir):
            return None
        cookies_files = [f for f in os.listdir(self.cookie_dir) if f.endswith(".txt")]
        if not cookies_files:
            return None
        return os.path.join(self.cookie_dir, random.choice(cookies_files))

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("Saving cookies from urls...")
        if not os.path.exists(self.cookie_dir):
            os.makedirs(self.cookie_dir)
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(urls):
                path = f"{self.cookie_dir}/cookie_{i}.txt"
                link = "https://batbin.me/api/v2/paste/" + url.split("/")[-1]
                async with session.get(link) as resp:
                    resp.raise_for_status()
                    with open(path, "wb") as fw:
                        fw.write(await resp.read())
        logger.info(f"Cookies saved in {self.cookie_dir}.")

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        try:
            _search = VideosSearch(query, limit=1)
            results = await _search.next()
            if results and results["result"]:
                data = results["result"][0]
                return Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name"),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")) if data.get("duration") else 0,
                    message_id=m_id,
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                    url=data.get("link"),
                    view_count=data.get("viewCount", {}).get("short"),
                    video=video,
                )
        except Exception as e:
            logger.error(f"Search error: {e}")
        return None

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list[Track]:
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist.get("videos", [])[:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")) if data.get("duration") else 0,
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                    url=data.get("link").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except Exception as e:
            logger.error(f"Playlist error: {e}")
        return tracks

    async def download_worker(self):
        while True:
            try:
                track = await self.download_queue.get()
                if not track.file_path:
                    await self.download(track.id, video=track.video)
                    downloaded = await db.get_downloaded(track.id)
                    if downloaded:
                        track.file_path = downloaded['file_path']
                self.download_queue.task_done()
            except Exception as e:
                logger.error(f"Download worker error: {e}")
                import traceback
                logger.error(traceback.format_exc())

    async def start_background_downloads(self):
        if self.download_task is None:
            self.download_task = asyncio.create_task(self.download_worker())

    async def queue_for_download(self, track: Track):
        await self.download_queue.put(track)

    async def download(self, video_id: str, video: bool = False) -> str | None:
        if not video_id or len(video_id) < 3:
            return None

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        ext = "mkv" if video else "webm"
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

        # Check if file exists locally first
        if os.path.exists(file_path):
            await db.add_downloaded(video_id, file_path, video)
            return file_path

        # Check database
        existing = await db.get_downloaded(video_id)
        if existing and os.path.exists(existing['file_path']):
            await db.update_last_used(video_id)
            return existing['file_path']

        try:
            # Create ssl context that doesn't check certs to avoid errors with render
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=ssl_context)
            ) as session:
                params = {
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "type": "video" if video else "audio",
                    "api_key": config.YOUTUBE_API_KEY
                }

                async with session.get(
                    f"{config.YOUTUBE_API_URL}/download",
                    params=params
                ) as response:
                    if response.status == 401:
                        logger.error("[API] Invalid API key")
                        return None
                    if response.status != 200:
                        logger.error(f"[API] returned {response.status}")
                        text = await response.text()
                        logger.error(text)
                        return None

                    # New API directly returns the file!
                    with open(file_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)

            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                await db.add_downloaded(video_id, file_path, video)
                return file_path
        except Exception as e:
            logger.error(f"Download exception for ID {video_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
        return None

