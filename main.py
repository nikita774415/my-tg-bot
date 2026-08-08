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

# ПРОСТОЙ И ОБЫЧНЫЙ СИСТЕМНЫЙ ПРОМПТ
SYSTEM_INSTRUCTION = (
    "Ты — обычный и вежливый автоответчик Никиты в Telegram.\n\n"
    "ПРАВИЛА ОБЩЕНИЯ:\n"
    "1. Отвечай кратко (1-2 предложения), спойкойно и по делу.\n"
    "2. Напиши, что Никита сейчас занят или отшел от телефона, но обязательно прочитает сообщение позже.\n"
    "3. Не отыгрывай никакие роли, не используй лишний сленг или излишний официоз.\n"
    "4. Если человек пишет что-то срочное, скажи, что передашь ему при первой возможности."
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
                max_tokens=60
            )
            
            reply_text = response.choices[0].message.content
            chat_histories[user_id].append({"role": "assistant", "content": reply_text})
            
            await event.reply(reply_text)
            
    except Exception as e:
        print(f"Ошибка при ответе: {e}")

print("Обычный автоответчик запущен!")
client_tg.start()
client_tg.run_until_disconnected()
