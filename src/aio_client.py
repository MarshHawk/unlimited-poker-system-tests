import aiohttp
import asyncio

async def main():
    session = aiohttp.ClientSession()
    async with session.ws_connect(
        "ws://127.0.0.1:3000/ws",
        headers={
            "Accept-Encoding": "gzip, deflate, br",
            "Pragma": "no-cache",
            "Sec-Websocket-Protocol": "graphql-ws",
        },
    ) as ws:
        print("yes")
        await ws.send_json(
            {
                "type": "connection_init",
                "payload": {"x-user-token": "sean", "x-table-token": "123"},
            }
        )

        async for msg in ws:
            print("message")
            print(msg.data)

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

            print("awaiting deal sub")

            await ws.send_json(deal_sub)
            print("I can do stuff here?")
            async for msg in ws:
                print(msg.data)

    await session.close()


asyncio.run(main())
