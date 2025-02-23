import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import AUTH_CHANNEL, LOG_CHANNEL, PICS
from plugins.dbusers import db
from Script import script
import random

logger = logging.getLogger(__name__)

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
            # Add more buttons for additional channels as needed
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

    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@SuperToppers')
            ],[
            InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/SuperToppers0'),
            InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ɢʀᴏᴜᴘ', url='https://t.me/SuperToppers')
            ],[
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
        ]]
        if CLONE_MODE == True:
            buttons.append([InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')])
        reply_markup = InlineKeyboardMarkup(buttons)
        me = client.me
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, me.mention),
            reply_markup=reply_markup
        )
        return

    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre

 = ""
    if data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>Invalid link or Expired link!</b>",
                protect_content=True
            )
        is_valid = await check_token(client, userid, token)
        if is_valid:
            await message.reply_text(
                text=f"<b>Hey {message.from_user.mention}, You are successfully verified! Now you have unlimited access for all files till today midnight.</b>",
                protect_content=True
            )
            await verify_user(client, userid, token)
        else:
            return await message.reply_text(
                text="<b>Invalid link or Expired link!</b>",
                protect_content=True
            )

@Client.on_callback_query(filters.regex("verify_subscription"))
async def verify_subscription(client, callback_query):
    user_id = callback_query.from_user.id
    if await check_subscription(client, user_id):
        await callback_query.answer("You are successfully verified!", show_alert=True)
        await callback_query.message.delete()
    else:
        await callback_query.answer("Please join all required channels before verifying.", show_alert=True)
