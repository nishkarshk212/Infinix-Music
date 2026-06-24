# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of InfinixMusic


import asyncio
import importlib
import os
from time import time

from pyrogram import idle

from Infinix import (anon, app, config, db,
                   logger, stop, userbot, yt)
from Infinix.plugins import all_modules


async def cleanup_task():
    while True:
        try:
            logger.info("Running daily cleanup...")
            
            # Cleanup old downloads from database
            await db.cleanup_old_downloads(days_old=7)
            
            # Cleanup old cache and download files
            for directory in ['cache', 'downloads']:
                if os.path.exists(directory):
                    cutoff = time() - (7 * 86400)  # 7 days
                    for filename in os.listdir(directory):
                        file_path = os.path.join(directory, filename)
                        if os.path.isfile(file_path):
                            if os.path.getmtime(file_path) < cutoff:
                                try:
                                    os.remove(file_path)
                                    logger.info(f"Removed old file: {file_path}")
                                except Exception as e:
                                    logger.error(f"Failed to remove {file_path}: {e}")
                                    
            logger.info("Daily cleanup completed!")
            
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
            
        # Wait 24 hours before next cleanup
        await asyncio.sleep(86400)


async def main():
    await db.connect()
    await app.boot()
    await userbot.boot()
    await anon.boot()

    for module in all_modules:
        importlib.import_module(f"Infinix.plugins.{module}")
    logger.info(f"Loaded {len(all_modules)} modules.")

    if config.COOKIES_URL:
        await yt.save_cookies(config.COOKIES_URL)

    sudoers = await db.get_sudoers()
    app.sudoers.update(sudoers)
    app.bl_users.update(await db.get_blacklisted())
    logger.info(f"Loaded {len(app.sudoers)} sudo users.")
    
    # Start background tasks
    asyncio.create_task(cleanup_task())

    await idle()
    await stop()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
