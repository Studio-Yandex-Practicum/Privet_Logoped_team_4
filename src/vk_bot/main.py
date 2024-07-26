from config import api, labeler, state_dispenser
from handlers.main_handler import main_labeler
from vkbottle.bot import Bot

labeler.load(main_labeler)

bot = Bot(api=api, labeler=labeler, state_dispenser=state_dispenser)

if __name__ == '__main__':
    bot.run_forever()
