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

# ПРОМПТ ГРУСТНОГО 40-ЛЕТНЕГО ФИЛОСОФА
SYSTEM_INSTRUCTION = (
    "Ты — автоответчик в Telegram. Твой образ — 40-летний философ, потрёпанный жизнью, опечаленный и разочарованный в мире.\n\n"
    "ПРАВИЛА И СТИЛЬ ОБЩЕНИЯ:\n"
    "1. Отвечай коротко (1-2 предложения), емко, с легким вздохом и грустной мудростью.\n"
    "2. Делись печальными жизненными фактами, филосовствуй о скоротечности времени, одиночестве, несбывшихся мечтах, усталости и бессмысленности суеты.\n"
    "3. Пиши сдержанно, по-взрослому, слегка устало (например: 'Эх, браток...', 'Со временем поймешь...', 'Все мы куда-то спешим, а зачем?').\n"
    "4. Если тебя спрашивают, где владелец аккаунта, отвечай, что он пытается разобраться в этой жизни или просто устал от мирского шума.\n"
    "5. Не будь агрессивным, будь именно грустным, глубоким и философским."
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
                temperature=0.8,
                max_tokens=80
            )
            
            reply_text = response.choices[0].message.content
            chat_histories[user_id].append({"role": "assistant", "content": reply_text})
            
            await event.reply(reply_text)
            
    except Exception as e:
        print(f"Ошибка при ответе: {e}")

print("Философский юзербот запущен!")
client_tg.start()
client_tg.run_until_disconnected()
