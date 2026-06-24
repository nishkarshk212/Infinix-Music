# Copyright (c) 2025 TheHamkerAlone 
# Licensed under the MIT License.
# This file is part of InfinixMusic


import pyrogram

from Infinix import config, logger


class Bot(pyrogram.Client):
    def __init__(self):
        super().__init__(
            name="Infinix",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            parse_mode=pyrogram.enums.ParseMode.HTML,
            max_concurrent_transmissions=7,
            link_preview_options=pyrogram.types.LinkPreviewOptions(is_disabled=True),
        )
        self.owner = config.OWNER_ID
        self.logger = config.LOGGER_ID
        self.bl_users = pyrogram.filters.user()
        self.sudoers = pyrogram.filters.user(self.owner)

    async def boot(self):
        """
        Starts the bot and performs initial setup.

        Raises:
            SystemExit: If the bot fails to access the log group or is not an administrator in the logger group.
        """
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name
        self.username = self.me.username
        self.mention = self.me.mention

        # Set bot commands for suggestions
        await self.set_bot_commands([
            pyrogram.types.BotCommand("start", "Start the bot"),
            pyrogram.types.BotCommand("help", "Show help menu"),
            pyrogram.types.BotCommand("play", "Play a song"),
            pyrogram.types.BotCommand("vplay", "Play a video"),
            pyrogram.types.BotCommand("pause", "Pause current track"),
            pyrogram.types.BotCommand("resume", "Resume paused track"),
            pyrogram.types.BotCommand("skip", "Skip to next track"),
            pyrogram.types.BotCommand("stop", "Stop playback"),
            pyrogram.types.BotCommand("queue", "Show current queue"),
            pyrogram.types.BotCommand("seek", "Seek to position"),
            pyrogram.types.BotCommand("ping", "Check bot latency"),
            pyrogram.types.BotCommand("stats", "Show bot stats"),
            pyrogram.types.BotCommand("settings", "Bot settings"),
            pyrogram.types.BotCommand("lang", "Change language"),
        ])

        try:
            await self.send_message(self.logger, "Bot Started")
            get = await self.get_chat_member(self.logger, self.id)
        except Exception as ex:
            raise SystemExit(f"Bot has failed to access the log group: {self.logger}\nReason: {ex}")

        if get.status != pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
            raise SystemExit("Please promote the bot as an admin in logger group.")
        logger.info(f"Bot started as @{self.username}")

    async def exit(self):
        """
        Asynchronously stops the bot.
        """
        await super().stop()
        logger.info("Bot stopped.")
