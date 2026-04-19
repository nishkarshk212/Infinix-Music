# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of AloneXMusic
# ALONE-CODER

from pyrogram import filters, types
from AloneX import app

@app.on_message(
    filters.command("alone")
    & filters.private
    & filters.user(6079943111)
)
async def alone_command(_, message: types.Message):
    await message.reply_video(
        video="https://files.catbox.moe/0n7rlf.mp4",
        caption="""**[ 🧟 ](https://t.me/XoDrk) нαϲкє𝚍 ву [ 🧟 ](https://t.me/XoDrk)**""",
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton(
                        "• нαϲкє𝚍 ву  •", url="https://t.me/XoDrk"
                    )
                ]
            ]
        ),
    )
