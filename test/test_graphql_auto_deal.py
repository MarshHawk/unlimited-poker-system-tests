import asyncio
import json
import uuid

import aiohttp
import pytest
import requests

GRAPHQL_URL = "http://localhost:3000/graphql"
WS_URL = "ws://127.0.0.1:3000/ws"
HTTP_TIMEOUT_SECONDS = 5
WS_CONNECT_TIMEOUT_SECONDS = 5


DEAL_SUBSCRIPTION = """
subscription DealSubscription($mutationType: MutationType) {
  deal(mutationType: $mutationType) {
    mutationType
    id
    deal {
      id
      tableId
    }
  }
}
"""


DEAL_MUTATION = """
mutation Deal($input: DealInput!) {
  deal(input: $input)
}
"""


PLAY_TURN_MUTATION = """
mutation PlayTurn($id: ID!, $playerId: ID!, $action: PlayerAction!, $amount: Decimal!) {
  playTurn(id: $id, playerId: $playerId, action: $action, amount: $amount)
}
"""


def graphql(query: str, variables: dict, headers: dict | None = None) -> dict:
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers=headers or {},
        timeout=HTTP_TIMEOUT_SECONDS,
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert "errors" not in payload, payload.get("errors")
    assert payload.get("data") is not None, payload
    return payload["data"]


async def wait_for_data(ws: aiohttp.ClientWebSocketResponse, timeout_seconds: int = 5) -> dict:
    ignored_count = 0
    last_payload = None
    while True:
        msg = await asyncio.wait_for(ws.receive(), timeout=timeout_seconds)
        assert msg.type == aiohttp.WSMsgType.TEXT, f"Unexpected ws message type: {msg.type}"
        payload = json.loads(msg.data)
        last_payload = payload
        msg_type = payload.get("type")
        if msg_type == "data":
            return payload
        if msg_type == "error":
            raise AssertionError(f"GraphQL subscription error: {payload}")
        ignored_count += 1
        if ignored_count >= 25:
            raise AssertionError(
                f"Timed out waiting for GraphQL data frame. Ignored {ignored_count} control frames. "
                f"Last payload: {last_payload}"
            )


async def wait_for_new_deal_event(
    ws: aiohttp.ClientWebSocketResponse,
    initial_hand_id: str,
    total_timeout_seconds: int = 10,
) -> dict:
    deadline = asyncio.get_running_loop().time() + total_timeout_seconds
    last_deal_id = None
    while True:
        remaining = deadline - asyncio.get_running_loop().time()
        if remaining <= 0:
            raise AssertionError(
                f"Timed out waiting for new deal id after {initial_hand_id}. Last observed deal id: {last_deal_id}"
            )
        event = await wait_for_data(ws, timeout_seconds=max(1, int(remaining)))
        deal_payload = event.get("payload", {}).get("data", {}).get("deal")
        if not deal_payload:
            continue
        last_deal_id = deal_payload.get("id")
        if last_deal_id and last_deal_id != initial_hand_id:
            return event


@pytest.mark.asyncio
async def test_deal_subscription_receives_next_hand_after_game_over():
    table_id = f"auto-deal-{uuid.uuid4().hex[:8]}"

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(
            WS_URL,
            timeout=aiohttp.ClientTimeout(total=WS_CONNECT_TIMEOUT_SECONDS, sock_connect=WS_CONNECT_TIMEOUT_SECONDS),
            headers={
                "Accept-Encoding": "gzip, deflate, br",
                "Pragma": "no-cache",
                "Sec-Websocket-Protocol": "graphql-ws",
            },
        ) as ws:
            # Init GraphQL-WS connection with explicit table token.
            await ws.send_json(
                {
                    "type": "connection_init",
                    "payload": {"x-user-token": "observer", "x-table-token": table_id},
                }
            )

            # Start deal subscription.
            await ws.send_json(
                {
                    "id": "deal-sub",
                    "type": "start",
                    "payload": {
                        "variables": {},
                        "extensions": {},
                        "operationName": "DealSubscription",
                        "query": DEAL_SUBSCRIPTION,
                    },
                }
            )

            # Trigger initial deal.
            deal_result = graphql(
                DEAL_MUTATION,
                {
                    "input": {
                        "tableId": table_id,
                        "players": [
                            {"id": "alice", "stack": "1000"},
                            {"id": "bob", "stack": "1000"},
                        ],
                    }
                },
            )
            initial_hand_id = deal_result["deal"]
            assert initial_hand_id

            first_deal_event = await wait_for_data(ws)
            first_payload = first_deal_event["payload"]["data"]["deal"]
            assert first_payload["id"] == initial_hand_id
            assert first_payload["deal"]["tableId"] == table_id

            # End the hand quickly: in heads-up preflop, SB/button (alice) acts first and can fold.
            play_result = graphql(
                PLAY_TURN_MUTATION,
                {
                    "id": initial_hand_id,
                    "playerId": "alice",
                    "action": "Fold",
                    "amount": "0",
                },
                headers={
                    "X-User-Token": "alice",
                    "X-Table-Token": table_id,
                    "X-Hand-Token": initial_hand_id,
                },
            )
            assert play_result["playTurn"] == initial_hand_id

            # Verify a NEW deal event is pushed automatically after game over.
            # Ignore duplicate/replayed events for the same hand id.
            second_deal_event = await wait_for_new_deal_event(ws, initial_hand_id)
            second_payload = second_deal_event["payload"]["data"]["deal"]
            next_hand_id = second_payload["id"]

            assert next_hand_id != initial_hand_id, "Expected auto-deal to create a new hand id"
            assert second_payload["deal"]["tableId"] == table_id
