# bot.py
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import config

bot = Client("mybot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)

def load_messages():
    with open("message.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

async def send_from_session(session_str, username, messages, index):
    results = []
    try:
        async with Client(session_name=None, session_string=session_str,
                          api_id=config.API_ID, api_hash=config.API_HASH) as app:
            user = await app.get_users(username)
            for i, msg in enumerate(messages, 1):
                await app.send_message(chat_id=user.id, text=msg)
                results.append(f"✅ Session {index}: মেসেজ {i} পাঠানো হয়েছে")
                await asyncio.sleep(1)
    except Exception as e:
        results.append(f"❌ Session {index} Error: {e}")
    return results

async def send_all_with_timeout(username, messages):
    tasks = [asyncio.create_task(send_from_session(s, username, messages, idx+1))
             for idx, s in enumerate(config.SESSIONS)]
    done, pending = await asyncio.wait(tasks, timeout=60)
    results = []
    for d in done:
        results.extend(d.result())
    for p in pending:
        p.cancel()
        results.append("⏰ Time limit reached. Cancelled remaining tasks.")
    return results

@bot.on_message(filters.command("send") & filters.private)
async def handler(c: Client, m: Message):
    parts = m.text.split()
    if len(parts) != 2:
        await m.reply("⚠️ সঠিক ব্যবহার: /send @username")
        return
    username = parts[1].lstrip("@")
    messages = load_messages()
    await m.reply(f"🚀 @{username} কে ৩টি session দিয়ে মেসেজ পাঠানো শুরু হলো (১ মিনিট সময়সীমা)")
    result = await send_all_with_timeout(username, messages)
    await m.reply("\n".join(result))

if __name__ == "__main__":
    bot.run()