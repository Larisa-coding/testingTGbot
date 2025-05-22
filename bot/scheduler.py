from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from database import get_unnotified_participants, mark_reminder_sent
from config import EVENT_DATE
import asyncio

async def check_reminders(bot):
    now = datetime.now()
    delta = EVENT_DATE - now
    if delta > timedelta(hours=23, minutes=59):
        return

    participants = await get_unnotified_participants()
    for p in participants:
        try:
            await bot.send_message(p["telegram_user_id"], "Напоминаем: завтра состоится мероприятие «Бег, Кофе, Танцы»! Ждём вас!")
            await mark_reminder_sent(p["telegram_user_id"])
        except Exception as e:
            print(f"Error sending to {p['telegram_user_id']}: {e}")
        await asyncio.sleep(0.1)

def setup_scheduler(bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_reminders, 'interval', minutes=30, args=(bot,))
    scheduler.start()