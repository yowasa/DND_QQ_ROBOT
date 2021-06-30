import hoshino
import asyncio

bot = hoshino.init()
app = bot.server_app

if __name__ == '__main__':
    bot.run(use_reloader=False, loop=asyncio.get_event_loop())
