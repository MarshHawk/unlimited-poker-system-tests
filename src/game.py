import asyncio
import aiohttp
from .models import deal_subscription

async def init_subscription_socket(user_name):
    session = aiohttp.ClientSession()
    async with session.ws_connect(
        "ws://127.0.0.1:8097/ws",
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

async def subscribe_to_deal(ws, user_name):
    deal_sub = {
        "id": "1",
        "type": "start",
        "payload": {
            "variables": {},
            "extensions": {},
            "operationName": "DealSubscription",
            "query": deal_subscription,
        },
    }
    await ws.send_json(deal_sub)
    async for msg in ws:
        print(msg.data)
        # TODO: assert
        return msg.data
    