import asyncio
import os
import time
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from groq import Groq

# Теперь бот будет брать ключи из "секретов" Koyeb
TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🚀 Бот успешно запущен в облаке! Жду голосовое.")

@dp.message(F.voice | F.video_note)
async def handle_audio(message: types.Message):
    content = message.voice if message.voice else message.video_note
    status_msg = await message.answer("⚡ Расшифровываю...")
    temp_file = f"audio_{int(time.time())}.ogg"

    try:
        file = await bot.get_file(content.file_id)
        await bot.download_file(file.file_path, temp_file)

        with open(temp_file, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(temp_file, audio_file.read()),
                model="whisper-large-v3",
                language="ru",
                response_format="text"
            )

        if transcription:
            await message.reply(f"<b>Текст:</b>\n\n{transcription}", parse_mode="HTML")
        else:
            await message.reply("Не удалось распознать.")

    except Exception as e:
        await message.reply(f"⚠️ Ошибка: {str(e)}")
    
    finally:
        await status_msg.delete()
        if os.path.exists(temp_file):
            os.remove(temp_file)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())