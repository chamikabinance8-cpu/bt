import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

# ඔබගේ Bot Token සහ Channel ID මෙහි ඇතුළත් කරන්න
BOT_TOKEN = '8623156099:AAEO_Qtj9Br3u_Okwd9gO53DxkuPiQu0h8I'
CHANNEL_ID = '@-1003131855993'

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Bot Start Command
@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    welcome_message = (
        "🚀 *Welcome to AutoPost Pro*\n\n"
        "Send me your post details in this format:\n\n"
        "Your main message text goes here.\n"
        "---\n"
        "Button 1 | https://link1.com\n"
        "Button 2 | https://link2.com\n"
        "Button 3 | https://link3.com"
    )
    await message.reply(welcome_message)

# Handle incoming text messages
@dp.message(F.text)
async def process_post_data(message: types.Message):
    # Text එක සහ Buttons වෙන් කර ගැනීම
    if "---" not in message.text:
        await message.reply("⚠️ *Invalid Format!*\n\nPlease use `---` to separate your text and buttons.")
        return

    parts = message.text.split("---")
    post_text = parts[0].strip()
    buttons_section = parts[1].strip()

    loading_msg = await message.reply("⏳ *Processing buttons and preparing post...*")
    builder = InlineKeyboardBuilder()
    valid_buttons = 0

    # සෑම පේළියක්ම පරීක්ෂා කර බටන් නිර්මාණය කිරීම
    for line in buttons_section.split('\n'):
        if '|' in line:
            btn_text, url = [item.strip() for item in line.split('|', 1)]
            
            if url.startswith("http"):
                builder.button(text=btn_text, url=url)
                valid_buttons += 1

    if valid_buttons == 0:
        await loading_msg.edit_text("❌ *Error:* No valid buttons found. Check your links.")
        return

    # බටන් පෙළගස්වන ආකාරය (1 = එක පේළියකට එක බටන් එක බැගින්)
    # ඔබට එක පේළියට බටන් 2ක් අවශ්‍ය නම් මෙය builder.adjust(2) ලෙස වෙනස් කරන්න.
    builder.adjust(1)

    try:
        # Channel එකට යැවීම
        await bot.send_message(
            chat_id=CHANNEL_ID, 
            text=post_text, 
            reply_markup=builder.as_markup()
        )
        await loading_msg.edit_text("✅ *Post successfully published with multiple buttons!*")
        
    except Exception as e:
        await loading_msg.edit_text(f"❌ *Error publishing post:* Check if the bot is admin in the channel.")

# Bot Run කිරීම
async def main():
    print("Bot is running safely...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
