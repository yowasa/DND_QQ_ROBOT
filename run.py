import hoshino
import asyncio
import uvicorn

bot = hoshino.init()
app = bot.asgi

if __name__ == '__main__':
    uvicorn.run("run:app", host="127.0.0.1", port=8080, log_level="info",workers=4)
    # bot.run(use_reloader=False, loop=asyncio.get_event_loop())
