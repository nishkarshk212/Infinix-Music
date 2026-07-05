
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
        
        # First try to get download URL from Youtube API using /audio or /video endpoints
        api_download_url = None
        need_audio_extraction = False
        if config.YOUTUBE_API_KEY and config.YOUTUBE_API_URL:
            try:
                endpoint = "/video" if video else "/audio"
                logger.info(f"Trying to get download URL from YouTube API at {endpoint}")
                async with aiohttp.ClientSession() as session:
                    headers = {"X-API-Key": config.YOUTUBE_API_KEY}
                    async with session.get(
                        f"{config.YOUTUBE_API_URL}{endpoint}",
                        params={"id": video_id},
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30),
                        ssl=ssl_context
                    ) as resp:
                        if resp.status == 200:
                            content_type = resp.headers.get('Content-Type', '')
                            if 'application/json' in content_type:
                                json_data = await resp.json()
                                logger.info(f"API returned JSON: {json_data}")
                                if video:
                                    video_data = json_data.get("video", {})
                                    api_download_url = video_data.get("best_video", {}).get("url")
                                else:
                                    audio_data = json_data.get("audio", {})
                                    api_download_url = audio_data.get("best_audio", {}).get("url")
                                    # If no best_audio_url, use best_video_url and we'll extract audio
                                    if not api_download_url:
                                        api_download_url = audio_data.get("audio_streams", [{}])[0].get("url") if audio_data.get("audio_streams") else None
                                        if not api_download_url:
                                            video_endpoint = "/video"
                                            async with session.get(
                                                f"{config.YOUTUBE_API_URL}{video_endpoint}",
                                                params={"id": video_id},
                                                headers=headers,
                                                timeout=aiohttp.ClientTimeout(total=30),
                                                ssl=ssl_context
                                            ) as video_resp:
                                                if video_resp.status == 200:
                                                    video_json = await video_resp.json()
                                                    video_data = video_json.get("video", {})
                                                    api_download_url = video_data.get("best_video", {}).get("url")
                                                    if api_download_url:
                                                        need_audio_extraction = True
                                
                                if api_download_url:
                                    logger.info(f"Got download URL from YouTube API: {api_download_url}")
                        else:
                            logger.info(f"YouTube API returned status {resp.status}")
            except Exception as e:
                logger.info(f"YouTube API request failed: {e}")

        # Fallback to XBit API if Youtube API did not succeed
        if not api_download_url and config.XBIT_API_TOKEN and config.XBIT_API_URL:
            try:
                logger.info(f"Trying to get download URL from XBit API for video ID: {video_id}")
                xbit_endpoint = f"{config.XBIT_API_URL}/info/{video_id}"
                xbit_headers = {
                    "x-api-key": config.XBIT_API_TOKEN,
                    "Content-Type": "application/json"
                }
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        xbit_endpoint,
                        headers=xbit_headers,
                        timeout=aiohttp.ClientTimeout(total=20),
                        ssl=ssl_context
                    ) as resp:
                        if resp.status == 200:
                            xbit_data = await resp.json()
                            if xbit_data.get("status") == "success":
                                url_key = "video_url" if video else "audio_url"
                                api_download_url = xbit_data.get(url_key)
                                if api_download_url:
                                    logger.info(f"Got download URL from XBit API: {api_download_url}")
            except Exception as e:
                logger.error(f"XBit API request failed: {e}")

        try:
            # Get cookies if available
            cookies_file = self.get_cookies()
            logger.info(f"[DEBUG] Using cookies file: {cookies_file}")

            ydl_opts = {
                'format': 'bestvideo+bestaudio/best' if video else 'bestaudio/best',
                'outtmpl': file_path.replace('.mp3', '.%(ext)s') if not video else file_path,
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'cookiefile': cookies_file if cookies_file else None,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'geo_bypass_country': 'US',
            }
            if not video:
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            # If API provided a direct download URL, try to download it directly via HTTP
            if api_download_url:
                logger.info(f"Downloading direct URL from API: {api_download_url}")
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                    if config.XBIT_API_TOKEN and "xbitcode.com" in api_download_url:
                        headers["x-api-key"] = config.XBIT_API_TOKEN
                    
                    temp_file_path = file_path
                    if need_audio_extraction:
                        temp_file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}_temp.mp4")
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(api_download_url, headers=headers, timeout=aiohttp.ClientTimeout(total=600), ssl=ssl_context) as response:
                            if response.status == 200:
                                with open(temp_file_path, "wb") as f:
                                    async for chunk in response.content.iter_chunked(1024 * 1024):
                                        f.write(chunk)
                                if os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 1024:
                                    if need_audio_extraction:
                                        # Extract audio from video using FFmpeg
                                        logger.info("Extracting audio from downloaded video")
                                        loop = asyncio.get_event_loop()
                                        def extract_audio():
                                            import subprocess
                                            subprocess.run([
                                                'ffmpeg', '-i', temp_file_path,
                                                '-vn', '-acodec', 'libmp3lame', '-ab', '192k', '-ar', '44100',
                                                '-y', file_path
                                            ], check=True, capture_output=True)
                                        await loop.run_in_executor(None, extract_audio)
                                        os.remove(temp_file_path)
                                    
                                    if os.path.exists(file_path) and os.path.getsize(file_path) > 1024:
                                        logger.info(f"[DEBUG] Download complete via direct API URL, adding to DB")
                                        await db.add_downloaded(video_id, file_path, video)
                                        return file_path
                                else:
                                    logger.error("Downloaded file is empty or too small.")
                            else:
                                logger.error(f"Failed to download direct URL, status code: {response.status}")
                except Exception as e:
                    logger.error(f"Error downloading from direct API URL: {e}")
                
                logger.info("Direct download failed or skipped, falling back to standard yt-dlp")

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

