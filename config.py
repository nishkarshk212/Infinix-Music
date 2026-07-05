#ALONE CODER
from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.API_ID = int(getenv("API_ID", "17596251"))
        self.API_HASH = getenv("API_HASH", "e58343b4c0193e293e391daf97603fcd")

        self.BOT_TOKEN = getenv("BOT_TOKEN", None)
        self.MONGO_URL = getenv("MONGO_URL", None)

        self.LOGGER_ID = int(getenv("LOGGER_ID", 0))
        self.OWNER_ID = int(getenv("OWNER_ID", 0))
        
        self.SESSION1 = getenv("SESSION", None)
        self.SESSION2 = getenv("SESSION2", None)
        self.SESSION3 = getenv("SESSION3", None)

        self.SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/AloneUpdates")
        self.SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/AloneBotSupport")

        self.AUTO_END: bool = getenv("AUTO_END", "false").lower() in ["true", "1", "yes"]
        self.AUTO_LEAVE: bool = getenv("AUTO_LEAVE", "false").lower() in ["true", "1", "yes"]
        self.VIDEO_PLAY: bool = getenv("VIDEO_PLAY", "true").lower() in ["true", "1", "yes"]

        self.QUEUE_LIMIT = int(getenv("QUEUE_LIMIT", "50"))
        self.DURATION_LIMIT = int(getenv("DURATION_LIMIT", "5400"))
        self.PLAYLIST_LIMIT = int(getenv("PLAYLIST_LIMIT", "20"))
        self.YOUTUBE_API_KEY = getenv("YOUTUBE_API_KEY", "lily_dahNMcDNyCNkkV1hj6Yb7kIroBPxnkr")
        self.YOUTUBE_API_URL = getenv("YOUTUBE_API_URL", "https://youtube-api-saas-backend.onrender.com")
        self.XBIT_API_TOKEN = getenv("XBIT_API_TOKEN", None)
        self.XBIT_API_URL = getenv("XBIT_API_URL", None)
        self.SHRUTI_API_URL = getenv("SHRUTI_API_URL", "https://api.shrutibots.site")
        self.SHRUTI_API_KEY = getenv("SHRUTI_API_KEY", None)
        self.COOKIES_URL = [
            url for url in getenv("COOKIES_URL", "").split(" ")
            if url and "batbin.me" in url
        ]
        self.DEFAULT_THUMB = getenv("DEFAULT_THUMB", "https://te.legra.ph/file/3e40a408286d4eda24191.jpg")
        self.PING_IMG = getenv("PING_IMG", "https://files.catbox.moe/haagg2.png")
        self.START_IMG = getenv("START_IMG", "https://files.catbox.moe/zvziwk.jpg")

    def check(self):
        missing = []
        if not self.API_ID:
            missing.append("API_ID")
        if not self.API_HASH:
            missing.append("API_HASH")
        if not self.BOT_TOKEN:
            missing.append("BOT_TOKEN")
        if not self.MONGO_URL:
            missing.append("MONGO_URL")
        if not self.LOGGER_ID:
            missing.append("LOGGER_ID")
        if not self.OWNER_ID:
            missing.append("OWNER_ID")
        if not self.SESSION1:
            missing.append("SESSION1")
            
        if missing:
            raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")
