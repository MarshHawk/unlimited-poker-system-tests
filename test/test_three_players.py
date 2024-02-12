import asyncio
import json
import aiohttp
import pytest
from src.play import execute_play_hand

from src.deal import deal_subscription, execute_deal_mutation

async def deal(players, semaphore):
    print("deal awaiting semaphore")
    await asyncio.sleep(0.5)
    for _ in range(3):
        await semaphore.acquire()
    execute_deal_mutation(players)

async def play_turn(semaphore, next_range):
    print("play turn awaiting semaphore")
    await asyncio.sleep(0.5)
    for _ in range(next_range):
        await semaphore.acquire()

    # execute_deal_mutation(players)

async def subscribe(player, semaphore):
    #print("subscribe started")
    session = aiohttp.ClientSession()
    async with session.ws_connect(
        "ws://127.0.0.1:8097/ws",
        headers={
            "Accept-Encoding": "gzip, deflate, br",
            "Pragma": "no-cache",
            "Sec-Websocket-Protocol": "graphql-ws",
        },
    ) as ws:
        #print("connected")
        await ws.send_json(
            {
                "type": "connection_init",
                "payload": {"x-user-token": player, "x-table-token": "123"},
            }
        )
        #print("message")
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
        #print("awaiting deal sub")
        await ws.send_json(deal_sub)
        #print("I can do stuff here?")
        semaphore.release()
        print("semaphore released")
        async for msg in ws:
            data = json.loads(msg.data)
            if data["type"] == "data":
                current_players = data["payload"]["data"]["deal"]["deal"]["streetEvents"][0]["currentActivePlayers"]
                current_player = [p for p in current_players if p["id"] == player][0]
                hand_id = data["payload"]["data"]["deal"]["id"]
                #print(hand_id)
                # print(json.dumps(data["payload"]["data"]["deal"], indent=4))
                hand_player = [p for p in data["payload"]["data"]["deal"]["deal"]["players"] if p["id"] == player][0]
                print(f"Player: {current_player["id"]}")
                print(f"Stack: {current_player["stack"]}")
                print(f"Cards: {hand_player["cards"]}")
                # Player 3 logic
                if player == "player_three":
                    print("Player 3 logic")
                    assert current_player == { "id": "player_three",
                                               "bet": "0",
                                               "stack": "1000",
                                               "isInactive": False
                                             }
                    play_sub = {
                      "id": hand_id,
                      "type": "start",
                      "payload": {
                          "variables": {},
                          "extensions": {},
                          "operationName": "OnHandEvent",
                          "query": "subscription OnHandEvent($mutationType: MutationType) {\n  handEvent(mutationType: $mutationType) {\n    mutationType\n    handId\n    streetEvent {\n      streetType\n      currentActivePlayers {\n        id\n        bet\n        stack\n        isInactive\n        isBigBlind\n      }\n      pot\n    }\n    playerEvent {\n      playerId\n      action\n      amount\n      streetType\n      currentStack\n      currentPot\n    }\n    cards {\n      flop\n      turn\n      river\n    }\n  }\n}\n",
                      },
                    }
                    await ws.send_json(play_sub)
                    execute_play_hand(hand_id, player, "FOLD", 0.0)
                    print("executed play hand")
                    async for msg in ws:
                        print(msg.data)
                        print("play turn event received")
                    
                    #await play_turn()
                # Player 2 logic
                if player == "player_two":
                    #print("Player 2 logic")
                    assert current_player ==  {
                            "id": "player_two",
                            "bet": "20",
                            "stack": "980",
                            "isInactive": False
                        }
                    # await play_turn()
                # Player 1 logic
                if player == "player_one":
                    #print("Player 1 logic")
                    assert current_player ==  {
                            "id": "player_one",
                            "bet": "10",
                            "stack": "990",
                            "isInactive": False
                        }
                    #await play_turn()

        print("outside of messages")
                #await session.close()

@pytest.mark.asyncio
async def test_runs_in_a_loop():
    semaphore = asyncio.Semaphore(0)
    players = ['player_one', 'player_two', 'player_three']
    # print("before await")
    await asyncio.gather(deal(players, semaphore),subscribe(players[0], semaphore), subscribe(players[1], semaphore), subscribe(players[2], semaphore))
    

