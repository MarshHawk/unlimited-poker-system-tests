import requests

BASE_URL = "http://localhost:3000/graphql"


def graphql(query: str, variables: dict | None = None):
    resp = requests.post(BASE_URL, json={"query": query, "variables": variables or {}})
    assert resp.status_code == 200
    data = resp.json()
    assert "errors" not in data, data.get("errors")
    return data["data"]


DEAL_MUTATION = """
mutation Deal($input: DealInput!) {
  deal(input: $input)
}
"""

PLAY_TURN_MUTATION = """
mutation PlayTurn($input: PlayTurnInput!) {
  playTurn(input: $input)
}
"""

HAND_QUERY = """
query Hand($id: ID!) {
  hand(id: $id) {
    id
    buttonIndex
    smallBlindIndex
    bigBlindIndex
    streetEvents {
      streetType
      currentActivePlayers {
        id
        isBigBlind
      }
    }
  }
}
"""


def test_graphql_three_player_preflop_and_postflop_order():
    variables = {
        "input": {
            "tableId": "order-test-3",
            "buttonIndex": 2,
            "smallBlind": "10",
            "bigBlind": "20",
            "players": [
                {"id": "alice", "stack": "1000"},
                {"id": "bob", "stack": "1000"},
                {"id": "charlie", "stack": "1000"},
            ],
        }
    }
    data = graphql(DEAL_MUTATION, variables)
    hand_id = data["deal"]
    assert hand_id

    data = graphql(HAND_QUERY, {"id": hand_id})
    street_events = data["hand"]["streetEvents"]
    assert street_events[0]["streetType"] == "Preflop"
    preflop_order = [p["id"] for p in street_events[0]["currentActivePlayers"]]
    assert preflop_order == ["charlie", "alice", "bob"]

    # Preflop actions to reach flop
    graphql(PLAY_TURN_MUTATION, {"input": {"handId": hand_id, "playerId": "charlie", "action": "Bet", "amount": "20"}})
    graphql(PLAY_TURN_MUTATION, {"input": {"handId": hand_id, "playerId": "alice", "action": "Bet", "amount": "10"}})
    graphql(PLAY_TURN_MUTATION, {"input": {"handId": hand_id, "playerId": "bob", "action": "Check", "amount": "0"}})

    data = graphql(HAND_QUERY, {"id": hand_id})
    last_street = data["hand"]["streetEvents"][-1]
    assert last_street["streetType"] == "Flop"
    postflop_order = [p["id"] for p in last_street["currentActivePlayers"]]
    assert postflop_order == ["alice", "bob", "charlie"]


def test_graphql_heads_up_postflop_order():
    variables = {
        "input": {
            "tableId": "order-test-2",
            "buttonIndex": 0,
            "smallBlind": "10",
            "bigBlind": "20",
            "players": [
                {"id": "alice", "stack": "1000"},
                {"id": "bob", "stack": "1000"},
            ],
        }
    }
    data = graphql(DEAL_MUTATION, variables)
    hand_id = data["deal"]
    assert hand_id

    # Preflop: SB calls, BB checks
    graphql(PLAY_TURN_MUTATION, {"input": {"handId": hand_id, "playerId": "alice", "action": "Bet", "amount": "10"}})
    graphql(PLAY_TURN_MUTATION, {"input": {"handId": hand_id, "playerId": "bob", "action": "Check", "amount": "0"}})

    data = graphql(HAND_QUERY, {"id": hand_id})
    last_street = data["hand"]["streetEvents"][-1]
    assert last_street["streetType"] == "Flop"
    postflop_order = [p["id"] for p in last_street["currentActivePlayers"]]
    assert postflop_order == ["bob", "alice"]
