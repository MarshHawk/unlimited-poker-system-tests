import requests
import asyncio


def play_turn_payload(hand_id, player, action, amount):
    return {
        "operationName": "PlayTurn",
        "variables": {
            "id": hand_id,
            "playerId": player,
            "action": action,
            "amount": amount,
        },
        "query": "mutation PlayTurn($id: ID!, $playerId: ID!, $action: PlayerAction!, $amount: Decimal!) {\n  playTurn(id: $id, playerId: $playerId, action: $action, amount: $amount)\n}\n",
    }

def play_turn_headers(player, hand_id):
    return {"X-User-Token": player, "X-Table-Token": "123", "X-Hand-Token": hand_id}


def execute_play_hand(hand_id, player, action, amount, semaphore):
    print("executing play hand")
    # await asyncio.sleep(5)
    #print(play_turn_payload(hand_id, player, action, amount))
    play = requests.post(
        "http://localhost:8097/graphql",
        json=play_turn_payload(hand_id, player, action, amount),
        headers=play_turn_headers(player, hand_id),
    )

async def subscribe_to_play(ws, hand_id):
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
    async for msg in ws:
        print(msg.data)
        print("play turn")


