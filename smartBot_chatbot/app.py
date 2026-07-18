from aiohttp import web
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkAdapter, TurnContext
from botbuilder.schema import Activity
from bot.smart_bot import SmartBot
import asyncio

async def input_messages(req):
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    async def auxilary_func(turn_context):
        await SmartBot().on_turn(turn_context)
    try:
        await BotFrameworkAdapter(BotFrameworkAdapterSettings("", "")).process_activity(activity, auth_header, auxilary_func)
        return web.Response(status=202)
    except Exception as e:
        print(f"Exception: {e}")
        return web.Response(status=500, text=str(e))

APP = web.Application()
APP.router.add_post("/api/messages", input_messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=3978)
    except Exception as e:
        raise e
