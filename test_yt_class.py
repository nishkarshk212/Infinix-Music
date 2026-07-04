import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('/Users/botbot/Desktop/Infinix'))

# Create a minimal config object just for YouTube class
class MinimalConfig:
    def __init__(self):
        self.YOUTUBE_API_KEY = "lily_6ttewJtNQfKvIUUhV6mxKwRwEf0CxJhZ"

from Infinix.core.youtube import YouTube
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

async def test_yt_class():
    # Temporarily replace config with our minimal one
    from Infinix import config as original_config
    original_config.YOUTUBE_API_KEY = "lily_6ttewJtNQfKvIUUhV6mxKwRwEf0CxJhZ"
    
    yt = YouTube()
    
    # Test searching for a Hindi song
    print("Searching for Hindi song 'Kesariya'...")
    track = await yt.search("Kesariya", 0, video=False)
    
    if not track:
        print("No track found!")
        return
    
    print(f"Found track: {track.title} (ID: {track.id})")
    
    # Test downloading the track
    print("\nDownloading track...")
    file_path = await yt.download(track.id, video=False)
    
    if file_path:
        print(f"Download successful! File path: {file_path}")
        print(f"File size: {os.path.getsize(file_path)} bytes")
    else:
        print("Download failed!")

if __name__ == "__main__":
    asyncio.run(test_yt_class())
