import asyncio
import aiohttp
import pytest

from src.deal import deal_subscription, execute_deal_mutation

async def deal(players, semaphore):
    print("deal awaiting semaphore")
    await asyncio.sleep(0.5)
    for _ in range(3):
        await semaphore.acquire()
    execute_deal_mutation(players)

async def play_turn():
    print("play turn")

async def subscribe(user_name, semaphore):
    print("subscribe started")
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
        print("message")
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
        semaphore.release()
        print("semaphore released")
        #assert True == False
        async for msg in ws:
            print(msg.data)
            #print("am i waiting?")

@pytest.mark.asyncio
async def test_runs_in_a_loop():
    semaphore = asyncio.Semaphore(0)
    players = ['player_one', 'player_two', 'player_three']
    await asyncio.gather(deal(players, semaphore),subscribe(players[0], semaphore), subscribe(players[1], semaphore), subscribe(players[2], semaphore))
    #print(wss)
    #hand_id  = execute_deal_mutation(players)

