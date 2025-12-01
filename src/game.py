import asyncio
import aiohttp
from .deal import deal_subscription

async def init_subscription_socket(user_name):
    session = aiohttp.ClientSession()
    async with session.ws_connect(
        "ws://127.0.0.1:3000/ws",
        headers={
            "Accept-Encoding": "gzip, deflate, br",
            "Pragma": "no-cache",
            "Sec-Websocket-Protocol": "graphql-ws",
        },
    ) as ws:
        print("connected")
        await ws.send_json(
            {
                "type": "connection_init",
                "payload": {"x-user-token": user_name, "x-table-token": "123"},
            }
        )
    return ws