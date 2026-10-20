import asyncio
import logging
import time
import os
from collections import deque
from typing import Dict, Deque

from telethon import TelegramClient, events, errors
import config
import ai

# Loggerni sozlaymiz
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(name)s]: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("UserBot")

# ==================== HOLATLAR VA MA'LUMOTLAR XOTIRASI ====================
# Boshlang'ich holat: o'chiq
AI_ACTIVE = False

# Chatlar bo'yicha oxirgi 10 ta xabar tarixi: {chat_id: deque([...], maxlen=10)}
chat_histories: Dict[int, Deque[dict]] = {}

# Qo'lda javob berilganda jim turish vaqti: {chat_id: timestamp_until_silence}
silenced_chats: Dict[int, float] = {}

# Spamdan himoya: {chat_id: last_replied_timestamp}
last_reply_time: Dict[int, float] = {}

# Bir vaqtning o'zida bir xil chatga parallel so'rov ketib qolmasligi uchun Lock
chat_locks: Dict[int, asyncio.Lock] = {}


def get_history(chat_id: int) -> Deque[dict]:
    """Chat uchun tarix navbatini olish yoki yaratish."""
    if chat_id not in chat_histories:
        chat_histories[chat_id] = deque(maxlen=config.HISTORY_LIMIT)
    return chat_histories[chat_id]


def get_chat_lock(chat_id: int) -> asyncio.Lock:
    """Har bir chat uchun alohida asinxron blokirovka."""
    if chat_id not in chat_locks:
        chat_locks[chat_id] = asyncio.Lock()
    return chat_locks[chat_id]


async def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    session_path = os.path.join(base_dir, "userbot_session")

    if not config.TG_API_ID or not config.TG_API_HASH:
        logger.error("TG_API_ID yoki TG_API_HASH topilmadi! Iltimos, .env faylini tekshiring.")
        return

    # Telethon mijozini ulanish xatolarida avtomatik qayta ulanadigan parametrlar bilan yaratamiz
    client = TelegramClient(
        session_path,
        config.TG_API_ID,
        config.TG_API_HASH,
        connection_retries=None,      # Cheksiz qayta ulanish
        retry_delay=2,                # Ulanish uzilsa 2 soniyada qayta urinish
        auto_reconnect=True
    )
    await client.start()

    me = await client.get_me()
    logger.info("=" * 50)
    logger.info("Userbot muvaffaqiyatli ishga tushdi!")
    logger.info("Akkaunt egasi: %s (@%s) [ID: %s]", me.first_name, me.username, me.id)
    logger.info("DIQQAT: AI hozir o'chiq (OFF). Yoqish uchun 'Saved Messages' ga /ai on deb yozing.")
    logger.info("=" * 50)

    # ----------------------------------------------------
    # 1. Boshqaruv: Saved Messages (Saqlangan xabarlar)
    # ----------------------------------------------------
    @client.on(events.NewMessage(chats="me"))
    async def handle_control_commands(event):
        global AI_ACTIVE
        text = (event.raw_text or "").strip().lower()

        if text == "/ai on":
            AI_ACTIVE = True
            await event.reply("🤖 AI yordamchi yoqildi (ON).\nEndi shaxsiy xabarlarga avtomatik tezkor javob beradi.")
            logger.info("AI yoqildi (ON).")
        elif text == "/ai off":
            AI_ACTIVE = False
            await event.reply("💤 AI yordamchi o'chirildi (OFF).")
            logger.info("AI o'chirildi (OFF).")
        elif text == "/ai status":
            status_text = "🟢 Yoniq (Faol)" if AI_ACTIVE else "🔴 O'chiq (Nofaol)"
            allowed_info = "Hamma"
            if config.ALLOWED_USER_IDS or config.ALLOWED_USERNAMES:
                allowed_info = f"IDs: {list(config.ALLOWED_USER_IDS)}, Users: {list(config.ALLOWED_USERNAMES)}"
            stats = (
                f"📊 **AI Userbot Holati:**\n"
                f"• Holat: {status_text}\n"
                f"• Model: `{config.AI_MODEL}`\n"
                f"• Ruxsat berilganlar: `{allowed_info}`\n"
                f"• Xotiradagi chatlar: {len(chat_histories)} ta\n"
                f"• Jim rejimdagi chatlar: {len(silenced_chats)} ta\n\n"
                f"Yoqish: `/ai on` | O'chirish: `/ai off`"
            )
            await event.reply(stats)

    # ----------------------------------------------------
    # 2. Egasi (Men) shaxsiy chatga yozsa -> 10 daqiqa jim turish
    # ----------------------------------------------------
    @client.on(events.NewMessage(outgoing=True))
    async def handle_outgoing_message(event):
        if not event.is_private or event.chat_id == me.id:
            return

        chat_id = event.chat_id
        silence_until = time.time() + config.MANUAL_REPLY_SILENCE
        silenced_chats[chat_id] = silence_until

        if event.raw_text:
            get_history(chat_id).append({"role": "model", "text": event.raw_text})

        logger.info(
            "Chat %s ga qo'lda javob yozildi. AI shu chatda %s soniya jim turadi.",
            chat_id, config.MANUAL_REPLY_SILENCE
        )

    # ----------------------------------------------------
    # 3. Keluvchi xabarlarga AI orqali tezkor javob berish
    # ----------------------------------------------------
    @client.on(events.NewMessage(incoming=True))
    async def handle_incoming_message(event):
        global AI_ACTIVE

        # 1. Faqat shaxsiy chatlar
        if not event.is_private:
            return

        chat_id = event.chat_id
        sender_id = event.sender_id

        if sender_id == me.id:
            return

        if not AI_ACTIVE:
            return

        # 2. Ruxsat tekshiruvi (ALLOWED_USERS sozlangan bo'lsa)
        if config.ALLOWED_USER_IDS or config.ALLOWED_USERNAMES:
            sender = await event.get_sender()
            sender_username = (getattr(sender, "username", None) or "").lower()
            is_allowed = (
                sender_id in config.ALLOWED_USER_IDS or
                sender_username in config.ALLOWED_USERNAMES
            )
            if not is_allowed:
                return

        user_text = event.raw_text
        if not user_text:
            return

        # 3. Jim turish tekshiruvi
        now = time.time()
        silence_until = silenced_chats.get(chat_id, 0)
        if now < silence_until:
            get_history(chat_id).append({"role": "user", "text": user_text})
            return

        # Parallel xabarlar to'qnashmasligi uchun har bir chat uchun Lock
        lock = get_chat_lock(chat_id)
        if lock.locked():
            # Agar ayni paytda ushbu chatga javob tayyorlanayotgan bo'lsa, navbatga olamiz
            await lock.acquire()
            lock_acquired = True
        else:
            await lock.acquire()
            lock_acquired = True

        try:
            # Spam / flood oraliq vaqtini tekshiramiz
            current_now = time.time()
            last_reply = last_reply_time.get(chat_id, 0)
            time_since_last = current_now - last_reply
            if time_since_last < config.RATE_LIMIT_DELAY:
                await asyncio.sleep(config.RATE_LIMIT_DELAY - time_since_last)

            history = list(get_history(chat_id))

            # typing statusi fon rejimida uzluksiz ko'rinib turishi uchun vazifa yaratamiz
            typing_task = asyncio.create_task(client.action(chat_id, "typing"))

            # Tezkor AI javobini olish
            reply_text = await ai.get_reply(history=history, user_text=user_text)

            # Javob olingach typing vazifasini to'xtatamiz
            if not typing_task.done():
                typing_task.cancel()

            if not reply_text:
                return

            # Javob yuborish
            await event.reply(reply_text)

            # Tarixni va vaqtni yangilash
            hist = get_history(chat_id)
            hist.append({"role": "user", "text": user_text})
            hist.append({"role": "model", "text": reply_text})
            last_reply_time[chat_id] = time.time()

            logger.info("Chat %s ga tezkor javob yuborildi.", chat_id)

        except errors.FloodWaitError as e:
            logger.warning("Telegram FloodWait: %s soniya kutilmoqda.", e.seconds)
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.exception("Xatolik yuz berdi: %s", e)
        finally:
            if lock_acquired:
                lock.release()

    logger.info("Userbot tezkor rejimda xabarlarni kutmoqda...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Userbot to'xtatildi.")
