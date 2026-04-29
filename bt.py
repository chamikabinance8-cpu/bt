import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

# ==========================================
# ⚙️ ඔබේ ප්‍රධාන සැකසුම්
# ==========================================

# @BotFather ගෙන් ලබාගත් ඔබගේ අලුත් Bot Token එක මෙහි දාන්න
BOT_TOKEN = '8623156099:AAEO_Qtj9Br3u_Okwd9gO53DxkuPiQu0h8I' 

# ඔබේ Channel එකේ නිවැරදි ඉලක්කම් ID එක
CHANNEL_ID = '-1003880058993' 

# ඔබගේ පුද්ගලික Telegram User ID එක
MY_USER_ID = 6221106415  

# ==========================================
# 💰 ShrinkMe.io API සැකසුම්
# ==========================================
SHORTENER_API_URL = 'https://shrinkme.io/api'
SHORTENER_API_TOKEN = '3711789a1054f6a3b9350ea2573b848f0fe9c14a'

# ==========================================

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# --- සාමාන්‍ය ලින්ක් එක ShrinkMe හරහා Short කරන Function එක ---
async def get_shortened_url(long_url):
    params = {
        'api': SHORTENER_API_TOKEN,
        'url': long_url
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # URL එක සහ Token එක නිවැරදිව යැවීම
            async with session.get(SHORTENER_API_URL, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # API එකෙන් සාර්ථකව short link එක ලැබුණොත්
                    if data.get('status') == 'success' and 'shortenedUrl' in data:
                        return data['shortenedUrl']
                    else:
                        print(f"API Error message: {data}")
                else:
                    print(f"Server Error Code: {response.status}")
    except Exception as e:
        print(f"Error shortening URL: {e}")
    
    # දෝෂයක් ආවොත් මුල් ලින්ක් එකම return කරයි
    return long_url

# --- Bot Start Command ---
@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    if message.from_user.id != MY_USER_ID:
        await message.reply("⚠️ *Access Denied:* You are not authorized to use this bot.")
        return
        
    welcome_message = (
        "🚀 *Welcome to AutoPost Pro (ShrinkMe.io Mode)*\n\n"
        "Send me your post details in this format:\n\n"
        "Your main message text goes here. You can write multiple lines.\n"
        "---\n"
        "Button 1 | https://link1.com\n"
        "Button 2 | https://link2.com"
    )
    await message.reply(welcome_message)

# --- පණිවිඩ සැකසීම, ලින්ක් Short කිරීම සහ යැවීම ---
@dp.message(F.text)
async def process_post_data(message: types.Message):
    # ආරක්ෂක පරීක්ෂාව
    if message.from_user.id != MY_USER_ID:
        return 
    
    if "---" not in message.text:
        await message.reply("⚠️ *Invalid Format!*\n\nPlease use `---` to separate your text and buttons.")
        return

    parts = message.text.split("---")
    post_text = parts[0].strip()
    buttons_section = parts[1].strip()

    loading_msg = await message.reply("⏳ *Shortening URLs via ShrinkMe.io and preparing post...*")
    builder = InlineKeyboardBuilder()
    valid_buttons = 0

    # බටන් නිර්මාණය කිරීම සහ ලින්ක් Short කිරීම
    for line in buttons_section.split('\n'):
        if '|' in line:
            btn_text, url = [item.strip() for item in line.split('|', 1)]
            
            if url.startswith("http"):
                # ලින්ක් එක ShrinkMe API එකට යැවීම
                short_url = await get_shortened_url(url) 
                
                builder.button(text=btn_text, url=short_url)
                valid_buttons += 1

    if valid_buttons == 0:
        await loading_msg.edit_text("❌ *Error:* No valid buttons found. Check your links.")
        return

    # බටන් එකක් යට එකක් පෙළගැස්වීම
    builder.adjust(1)

    # Channel එකට පෝස්ට් කිරීම
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID, 
            text=post_text, 
            reply_markup=builder.as_markup()
        )
        await loading_msg.edit_text("✅ *Post successfully published with ShrinkMe! 💰*")
        
    except Exception as e:
        await loading_msg.edit_text(f"❌ *Error publishing post:* \n`{str(e)}`\n\nMake sure the bot is still an Admin in the channel.")

# --- Bot Run කිරීම ---
async def main():
    print("💰 ShrinkMe Ad-Enabled Bot is running...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
