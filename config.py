import re
import os
import logging
from os import environ
from Script import script
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from plugins.dbusers import db
import random

id_pattern = re.compile(r'^.\d+$')
logger = logging.getLogger(__name__)

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('AUTH_CHANNEL', '-1002253042763 -1002461765329').split()]
API_ID = int(environ.get("API_ID", "27589191"))
API_HASH = environ.get("API_HASH", "094c70fee92b47679abeeb0922e12440")
BOT_TOKEN = environ.get("BOT_TOKEN", "")
PICS = (environ.get('PICS', 'https://ibb.co/5X5VxXM9')).split()
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]
BOT_USERNAME = environ.get("BOT_USERNAME", "ToppersFilesStore_Bot")
PORT = environ.get("PORT", "8080")
CLONE_MODE = bool(environ.get('CLONE_MODE', False))
CLONE_DB_URI = environ.get("CLONE_DB_URI", "mongodb+srv://mihaja5084:yeIh95RrMkRNZ3It@cluster0.6voc3fm.mongodb.net/?retryWrites=true&w=majority")
CDB_NAME = environ.get("CDB_NAME", "clonetechvj")
DB_URI = environ.get("DB_URI", "mongodb+srv://mihaja5084:yeIh95RrMkRNZ3It@cluster0.6voc3fm.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = environ.get("DB_NAME", "techvjbotz")
AUTO_DELETE_MODE = bool(environ.get('AUTO_DELETE_MODE', True))
AUTO_DELETE = int(environ.get("AUTO_DELETE", "30"))
AUTO_DELETE_TIME = int(environ.get("AUTO_DELETE_TIME", "1800"))
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1002440042338"))
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
PUBLIC_FILE_STORE = is_enabled((environ.get('PUBLIC_FILE_STORE', "True")), True)
VERIFY_MODE = bool(environ.get('VERIFY_MODE', False))
SHORTLINK_URL = environ.get("SHORTLINK_URL", "")
SHORTLINK_API = environ.get("SHORTLINK_API", "")
VERIFY_TUTORIAL = environ.get("VERIFY_TUTORIAL", "")
WEBSITE_URL_MODE = bool(environ.get('WEBSITE_URL_MODE', False))
WEBSITE_URL = environ.get("WEBSITE_URL", "https://supertoppersteam.blogspot.com/2025/02/supertoppers.html")
STREAM_MODE = bool(environ.get('STREAM_MODE', False))
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False
URL = environ.get("URL", "https://testofvjfilter-1fa60b1b8498.herokuapp.com/")

async def check_subscription(client, user_id):
    for channel in AUTH_CHANNEL:
        try:
            chat_member = await client.get_chat_member(channel, user_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            logger.error(f"Error checking subscription for {user_id} in {channel}: {e}")
            return False
    return True

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    user_id = message.from_user.id

    # Check if the user is subscribed to all required channels
    if not await check_subscription(client, user_id):
        # Create buttons for each required channel
        buttons = [
            [InlineKeyboardButton("Join Channel 1", url='https://t.me/SuperToppersChannel')],
            [InlineKeyboardButton("Join Channel 2", url='https://t.me/SuperToppersGroupp')],
            [InlineKeyboardButton("Verify Subscription", callback_data="verify_subscription")]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply("You need to subscribe to the required channels to use this bot. Please join the channels below and then click Verify Subscription:", reply_markup=reply_markup)
        return

    # User is subscribed to all required channels
    username = client.me.username
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(message.from_user.id, message.from_user.mention))

    buttons = [[
        InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@SuperToppers')
        ],[
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/SuperToppers0'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ɢʀᴏᴜᴘ', url='https://t.me/SuperToppers')
        ],[
        InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
        InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
    ]]
    if CLONE_MODE:
        buttons.append([InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')])
    reply_markup = InlineKeyboardMarkup(buttons)
    me = client.me
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=script.START_TXT.format(message.from_user.mention, me.mention),
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex("verify_subscription"))
async def verify_subscription(client, callback_query):
    user_id = callback_query.from_user.id
    if await check_subscription(client, user_id):
        await callback_query.answer("You are successfully verified!", show_alert=True)
        await callback_query.message.delete()
    else:
        await callback_query.answer("Please join all required channels before verifying.", show_alert=True)

@Client.on_message(filters.command("verify") & filters.incoming)
async def verify(client, message):
    user_id = message.from_user.id
    if await check_subscription(client, user_id):
        await message.reply("You are already subscribed to the required channels.")
    else:
        buttons = [
            [InlineKeyboardButton("Join Channel 1", url='https://t.me/SuperToppersChannel')],
            [InlineKeyboardButton("Join Channel 2", url='https://t.me/SuperToppersGroupp')],
            [InlineKeyboardButton("Verify Subscription", callback_data="verify_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply("You need to subscribe to the required channels to use this bot. Please join the channels below and then click Verify Subscription:", reply_markup=reply_markup)
