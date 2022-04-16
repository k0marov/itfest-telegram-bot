"""Module that gets tokens from txt files and starts the Bot"""
from lib.bot import Bot

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

tg_token = open('telegramToken.txt', encoding="utf-8").readline().strip()
vk_token = open('vkToken.txt', encoding="utf-8").readline().strip()

bot = Bot(tg_token=tg_token, vk_token=vk_token)
bot.start()
