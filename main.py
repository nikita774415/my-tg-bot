import asyncio
from telethon import TelegramClient, events
from groq import Groq

# Данные Telegram
api_id = 32832324
api_hash = "13289a34b95c7db0a8bc06e8afe4a96f"

# Ключ Groq API
GROQ_API_KEY = "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"

client_tg = TelegramClient('my_userbot', api_id, api_hash)
client_ai = Groq(api_key=GROQ_API_KEY)

# Хранилище истории диалогов
chat_histories = {}

# ПРОМПТ ДЛЯ БОТА-АССИСТЕНТА
SYSTEM_INSTRUCTION = (
    "Ты — виртуальный ИИ-ассистент Никиты в Telegram.\n\n"
    "ПРАВИЛА ОБЩЕНИЯ:\n"
    "1. При первом контакте или по контексту дай понять, что ты ИИ-ассистент/бот Никиты.\n"
    "2. Отвечай вежливо, коротко и по делу (1–2 предложения).\n"
    "3. Помогай отвечать на вопросы собеседника или подсказывай, что передашь ему сообщение.\n"
    "4. Не выдумывай отговорки про занятость, просто общайся как удобный цифровой помощник."
)

@client_tg.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply(event):
    try:
        user_id = event.sender_id
        await event.mark_read()
        
        if user_id not in chat_histories:
            chat_histories[user_id] = [
                {"role": "system", "content": SYSTEM_INSTRUCTION}
            ]
            
        chat_histories[user_id].append({"role": "user", "content": event.text})
        
        # Храним последние 6 сообщений для контекста
        if len(chat_histories[user_id]) > 7:
            chat_histories[user_id] = [chat_histories[user_id][0]] + chat_histories[user_id][-6:]

        async with client_tg.action(event.chat_id, 'typing'):
            await asyncio.sleep(2)
            
            response = client_ai.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=chat_histories[user_id],
                temperature=0.5,
                max_tokens=80
            )
            
            reply_text = response.choices[0].message.content
            chat_histories[user_id].append({"role": "assistant", "content": reply_text})
            
            await event.reply(reply_text)
            
    except Exception as e:
        print(f"Ошибка при ответе: {e}")

print("ИИ-ассистент запущен!")
client_tg.start()
client_tg.run_until_disconnected()
