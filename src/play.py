import requests

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
    return {"x-user-token": player, "x-table-token": "123", "x-hand-token": hand_id}


def execute_play_hand(hand_id, player, action, amount):
    play = requests.post(
        "http://localhost:8097/graphql",
        json=play_turn_payload(hand_id, player, action, amount),
        headers=play_turn_headers(player, hand_id),
    )
    print(play.json())