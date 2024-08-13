import logging
import asyncio
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .config import tg_token


logging.basicConfig(level=logging.INFO)
bot = Bot(token=tg_token)
scheduler = AsyncIOScheduler()

async def main():
    scheduler.start()

if __name__ == '__main__':
    asyncio.run(main())