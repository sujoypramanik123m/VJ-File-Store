import os
import logging
import random
import asyncio
from validators import domain
from Script import script
from plugins.dbusers import db
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import verify_user, check_token, check_verification, get_token
from config import AUTH_CHANNEL

logger = logging.getLogger(__name__)
BATCH_FILES = {}

async def is_subscribed(bot, query, channel):
    btn = []
    for id in channel:
        chat = await bot.get_chat(int(id))
        try:
            await bot.get_chat_member(id, query.from_user.id)
        except UserNotParticipant:
            btn.append([InlineKeyboardButton(f'Join {chat.title}', url=chat.invite_link)])
        except Exception as e:
            logger.error(f"Error checking chat member: {e}")
    return btn

def get_size(size):
    """Get size in readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units)-1:
        i += 1
        size /= 1024.0
    return f"{size:.2f} {units[i]}"

def format_file_name(file_name):
    chars = ["[", "]", "(", ")"]
    for c in chars:
        file_name = file_name.replace(c, "")
    file_name = '@SuperToppers ' + ' '.join(filter(lambda x: not x.startswith(('http', '@', 'www.')), file_name.split()))
    return file_name

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if AUTH_CHANNEL:
        try:
            btn = await is_subscribed(client, message, AUTH_CHANNEL)
            if btn:
                username = (await client.get_me()).username
                if len(message.command) > 1:
                    btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start={message.command[1]}")])
                else:
                    btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start=true")])
                await message.reply_text(
                    text=f"<b>👋 Hello {message.from_user.mention},\n\nPlease join the channel then click on the try again button. 😇</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
        except Exception as e:
            logger.error(f"Error in subscription check: {e}")
            return

    # Check if user exists in the database
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(message.from_user.id, message.from_user.mention))

    # Button creation
    buttons = [
        [InlineKeyboardButton('💝 Subscribe My YouTube Channel', url='https://youtube.com/@SuperToppers')],
        [InlineKeyboardButton('🔍 Support Group', url='https://t.me/SuperToppers0'),
         InlineKeyboardButton('🤖 Update Channel', url='https://t.me/SuperToppers')],
        [InlineKeyboardButton('💁‍♀️ Help', callback_data='help'),
         InlineKeyboardButton('😊 About', callback_data='about')]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    me = client.me
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=script.START_TXT.format(message.from_user.mention, me.mention),
        reply_markup=reply_markup
    )
