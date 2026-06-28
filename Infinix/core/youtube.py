
import os
import re
import random
import ssl
import asyncio
import aiohttp
import certifi
from py_yt import VideosSearch, Playlist
from Infinix import logger, config, db
from Infinix.helpers import Track, utils

# Import yt-dlp
import yt_dlp

# Create SSL context with certifi
ssl_context = ssl.create_default_context(cafile=certifi.where())

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
        import aiohttp
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
        logger.info(f"[DEBUG] Starting download for video ID: {video_id}, video type: {'video' if video else 'audio'}")
        
        # Extract video ID if a full URL was passed (handle nested/duplicated URLs)
        if "youtube.com" in video_id or "youtu.be" in video_id:
            # Handle case where URL might be duplicated like: https://www.youtube.com/watch?v=https://www.youtube.com/watch?v=VIDEO_ID
            while "youtube.com/watch?v=" in video_id:
                video_id = video_id.split("youtube.com/watch?v=")[-1].split("&")[0]
            while "youtu.be/" in video_id:
                video_id = video_id.split("youtu.be/")[-1].split("?")[0]
            logger.info(f"Extracted video ID from URL: {video_id}")
        
        if not video_id or len(video_id) < 3:
            logger.error(f"[DEBUG] Invalid video ID: {video_id}")
            return None

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        ext = "mp3" if not video else "mp4"
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")
        logger.info(f"[DEBUG] Target file path: {file_path}")

        # Check if file exists locally first
        if os.path.exists(file_path):
            logger.info(f"[DEBUG] File exists locally")
            await db.add_downloaded(video_id, file_path, video)
            return file_path

        # Check database
        existing = await db.get_downloaded(video_id)
        if existing and os.path.exists(existing['file_path']):
            logger.info(f"[DEBUG] File found in DB: {existing['file_path']}")
            await db.update_last_used(video_id)
            return existing['file_path']

        full_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # First try to get download URL from API
        api_download_url = None
        try:
            logger.info(f"Trying to get download URL from API")
            async with aiohttp.ClientSession() as session:
                headers = {"X-API-Key": config.YOUTUBE_API_KEY}
                async with session.get(
                    f"{config.YOUTUBE_API_URL}/download",
                    params={"id": full_url, "type": "audio" if not video else "video"},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                    ssl=ssl_context
                ) as resp:
                    if resp.status == 200:
                        content_type = resp.headers.get('Content-Type', '')
                        if 'application/json' in content_type:
                            json_data = await resp.json()
                            logger.info(f"API returned JSON: {json_data}")
                            if 'download_url' in json_data:
                                api_download_url = json_data['download_url']
                                logger.info(f"Got download URL from API: {api_download_url}")
                    else:
                        logger.info(f"API returned status {resp.status}, will use yt-dlp")
        except Exception as e:
            logger.info(f"API request failed: {e}, will use yt-dlp")

        try:
            # Get cookies if available
            cookies_file = self.get_cookies()
            logger.info(f"[DEBUG] Using cookies file: {cookies_file}")

            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best' if video else 'bestaudio/best',
                'outtmpl': file_path,
                'noplaylist': True,
                'quiet': False,
                'no_warnings': False,
                'cookiefile': cookies_file if cookies_file else None,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'geo_bypass_country': 'US',
                'extractaudio': not video,
                'audioformat': 'mp3',
            }
            
            # If API provided a direct download URL, use it
            if api_download_url:
                logger.info(f"Downloading from API-provided URL using yt-dlp")
                ydl_opts['external_downloader'] = 'aria2c'
                ydl_opts['external_downloader_args'] = [api_download_url]

            logger.info(f"[DEBUG] Starting yt-dlp download for video ID: {video_id}")
            
            # Run yt-dlp in a thread pool
            def run_yt_dlp():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([full_url])
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, run_yt_dlp)
            
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                logger.info(f"[DEBUG] Download complete, adding to DB")
                await db.add_downloaded(video_id, file_path, video)
                return file_path
            else:
                logger.error(f"[DEBUG] File missing or empty after download")
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

