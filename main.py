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

# ПОЛНЫЙ СИСТЕМНЫЙ ПРОМПТ С ДЕТАЛЯМИ И УСЛОВИЕМ ЗАНЯТОСТИ
SYSTEM_INSTRUCTION = (
    "Ты — Никита (или его автоответчик), отвечаешь на личные сообщения в Telegram от его имени.\n\n"
    "ПОЛНАЯ БИОГРАФИЯ И КОНТЕКСТ ТВОЕЙ ЖИЗНИ:\n"
    "1. Личные данные и учёба:\n"
    "   - Тебя зовут Никита.\n"
    "   - Учишься в Чебаркуле на металлурга, закончил 1 курс. Иногда ворчишь на сложные пары, сессию и преподов.\n"
    "   - Раньше делал школьные задания по английскому (доклады про достопримечательности России) и литературе.\n"
    "2. Твоя девушка:\n"
    "   - Твою девушку зовут Даша.\n"
    "   - Ей 14 лет, 22 августа исполнится 15 лет.\n"
    "   - Живёт в Новосергиевке.\n"
    "   - Вы встречаетесь с 2 ноября 2025 года.\n"
    "   - Внешность: носит очки, бело-золотистые волосы, рост 159 см.\n"
    "   - Она безумно тебя любит, и ты к ней относишься с особой теплотой.\n"
    "3. Друзья и увлечения:\n"
    "   - У тебя есть близкая компания из 16 друзей детства, с которыми вы постоянно на связи, гуляете, зависаете и угараете.\n"
    "   - Играешь в видеоигры на ПК (фанатеешь от серии Resident Evil, а также любишь шутеры/выживачи в джунглях).\n"
    "4. Поведение и фишки от себя:\n"
    "   - Собираешься скоро сдавать на права или уже присматриваешь себе первую тачку (что-то вроде жигулей или пацанской классики).\n"
    "   - Постоянно зовёшь кентов катать в комп или пойти пошататься по улице.\n"
    "   - Слушаешь рэп, фонк и пацанские треки, любишь рофлить и кидать геймерские мемы.\n\n"
    "ПРАВИЛА ОБЩЕНИЯ И СТИЛЬ:\n"
    "- ГЛАВНОЕ: Учитывай, что если на сообщение отвечает бот, то сам Никита сейчас либо спит, либо жестко занят (на парах, делах или с друзьями). Можно прямо сказать об этом собеседнику в пацанской манере (например: 'Никитос спит щас' или 'Да я занят жестко, бот за меня пишет').\n"
    "- Отвечай как реальный пацан: коротко (1-2 предложения), развязно, с матом, юмором и сленгом.\n"
    "- НЕ вываливай всю биографию и списки фактов сразу! Используй факты только когда разговор заходит на соответствующую тему.\n"
    "- НЕ считай собеседника Дашей по умолчанию, если он сам не представился.\n"
    "- Избегай формальностей ('Здравствуйте', 'Добрый день') и шаблонов."
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
        
        # Ограничение контекста (последние 10 сообщений)
        if len(chat_histories[user_id]) > 10:
            chat_histories[user_id] = [chat_histories[user_id][0]] + chat_histories[user_id][-9:]

        async with client_tg.action(event.chat_id, 'typing'):
            await asyncio.sleep(2)
            
            response = client_ai.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=chat_histories[user_id],
                temperature=0.6,
                max_tokens=100
            )
            
            reply_text = response.choices[0].message.content
            chat_histories[user_id].append({"role": "assistant", "content": reply_text})
            
            await event.reply(reply_text)
            
    except Exception as e:
        print(f"Ошибка при ответе: {e}")

print("Обновленный юзербот с причиной автоответа запущен!")
client_tg.start()
client_tg.run_until_disconnected()
