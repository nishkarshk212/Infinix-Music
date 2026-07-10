# Copyright (c) 2025 TheHamkerAlone
# Licensed under the MIT License.
# This file is part of InfinixMusic
# ALONE-CODER

import asyncio
from pathlib import Path

from pyrogram import filters, types

from Infinix import anon, app, config, db, lang, logger, queue, tg, yt
from Infinix.helpers import buttons, utils
from Infinix.helpers._play import checkUB

# Track active background download tasks to avoid duplicates
_background_tasks: set[str] = set()


async def _background_download_task(track) -> None:
    """
    Background task for a queued track:
      1. Get stream URL immediately (so it can play without delay when its turn comes).
      2. Download the actual file in the background (for cleanup + reliability).
    """
    try:
        if not getattr(track, "stream_url", None) and not track.file_path:
            stream_url = await yt.get_stream_url(track.id, video=track.video)
            if stream_url:
                track.stream_url = stream_url
                logger.info("Background: stream URL ready for %s", track.id)

        if not track.file_path:
            path = await yt.download(track.id, video=track.video)
            if path:
                track.file_path = path
                logger.info("Background: file download complete for %s → %s", track.id, path)
            else:
                logger.warning("Background: file download failed for %s — will use stream URL", track.id)
    except Exception as e:
        logger.warning("Background download task failed for %s: %s", track.id, e)


def _start_background_download(track) -> None:
    """Start a background download task for a queued track (skips duplicates)."""
    if track.id not in _background_tasks:
        _background_tasks.add(track.id)
        task = asyncio.create_task(_background_download_task(track))
        task.add_done_callback(lambda _: _background_tasks.discard(track.id))


def playlist_to_queue(chat_id: int, tracks: list) -> str:
    text = "<blockquote expandable>"
    for track in tracks:
        pos = queue.add(chat_id, track)
        text += f"<b>{pos}.</b> {track.title}\n"
        _start_background_download(track)
    text = text[:1948] + "</blockquote>"
    return text


@app.on_message(
    filters.command(["play", "playforce", "vplay", "vplayforce"])
    & filters.group
    & ~app.bl_users
)
@lang.language()
@checkUB
async def play_hndlr(
    _,
    m: types.Message,
    force: bool = False,
    m3u8: bool = False,
    video: bool = False,
    url: str = None,
) -> None:
    sent = await m.reply_text(m.lang["play_searching"])
    file = None
    mention = m.from_user.mention
    media = tg.get_media(m.reply_to_message) if m.reply_to_message else None
    tracks = []

    if url:
        if "playlist" in url:
            await sent.edit_text(m.lang["playlist_fetch"])
            tracks = await yt.playlist(
                config.PLAYLIST_LIMIT, mention, url, video
            )
            if not tracks:
                return await sent.edit_text(m.lang["playlist_error"])
            file = tracks[0]
            tracks.remove(file)
            file.message_id = sent.id
        else:
            file = await yt.search(url, sent.id, video=video)

        if not file:
            return await sent.edit_text(
                m.lang["play_not_found"].format(config.SUPPORT_CHAT)
            )

    elif len(m.command) >= 2:
        query = " ".join(m.command[1:])
        file = await yt.search(query, sent.id, video=video)
        if not file:
            return await sent.edit_text(
                m.lang["play_not_found"].format(config.SUPPORT_CHAT)
            )

    elif media:
        setattr(sent, "lang", m.lang)
        file = await tg.download(m.reply_to_message, sent)

    if not file:
        return await sent.edit_text(m.lang["play_usage"])

    if file.duration_sec > config.DURATION_LIMIT:
        return await sent.edit_text(
            m.lang["play_duration_limit"].format(config.DURATION_LIMIT // 60)
        )

    if await db.is_logger():
        await utils.play_log(m, file.title, file.duration)

    file.user = mention

    if force:
        queue.force_add(m.chat.id, file)
    else:
        position = queue.add(m.chat.id, file)

        if position != 0 or await db.get_call(m.chat.id):
            await sent.edit_text(
                m.lang["play_queued"].format(
                    position,
                    file.url,
                    file.title,
                    file.duration,
                    m.from_user.mention,
                ),
                reply_markup=buttons.play_queued(
                    m.chat.id, file.id, m.lang["play_now"]
                ),
            )
            # Start background: get stream URL + download file for this queued song
            _start_background_download(file)

            if tracks:
                added = playlist_to_queue(m.chat.id, tracks)
                await app.send_message(
                    chat_id=m.chat.id,
                    text=m.lang["playlist_queued"].format(len(tracks)) + added,
                )
            return

    # ── Immediate play: get stream URL for instant playback ───────────────────
    if not getattr(file, "stream_url", None) and not file.file_path:
        file.stream_url = await yt.get_stream_url(file.id, video=video)

        if not getattr(file, "stream_url", None):
            fname = f"downloads/{file.id}.{'mp4' if video else 'webm'}"
            if Path(fname).exists():
                file.file_path = fname
            else:
                await sent.edit_text(m.lang["play_downloading"])
                file.file_path = await yt.download(file.id, video=video)

    await anon.play_media(chat_id=m.chat.id, message=sent, media=file)

    if tracks:
        added = playlist_to_queue(m.chat.id, tracks)
        await app.send_message(
            chat_id=m.chat.id,
            text=m.lang["playlist_queued"].format(len(tracks)) + added,
        )
