import requests

BASE_URL = "http://localhost:3000/graphql"


def graphql(query: str, variables: dict | None = None):
    resp = requests.post(BASE_URL, json={"query": query, "variables": variables or {}})
    assert resp.status_code == 200
    data = resp.json()
    assert "errors" not in data, data.get("errors")
    return data["data"]


def test_graphql_deal_includes_rules():
    deal_mutation = """
    mutation Deal($input: DealInput!) {
      deal(input: $input)
    }
    """
    variables = {
        "input": {
            "tableId": "rules-test",
            "players": [
                {"id": "alice", "stack": "1000"},
                {"id": "bob", "stack": "1000"},
            ],
        }
    }
    data = graphql(deal_mutation, variables)
    hand_id = data["deal"]
    assert hand_id

    hand_query = """
    query Hand($id: ID!) {
      hand(id: $id) {
        id
        rules {
          name
          holeCards
          flopCards
          turnCards
          riverCards
          totalBoardCards
          streets
          btnFirstPostflop
        }
      }
    }
    """
    data = graphql(hand_query, {"id": hand_id})
    rules = data["hand"]["rules"]

    assert rules["name"] == "HOLDEM_RULES"
    assert rules["holeCards"] == 2
    assert rules["flopCards"] == 3
    assert rules["turnCards"] == 1
    assert rules["riverCards"] == 1
    assert rules["totalBoardCards"] == 5
    assert rules["streets"] == ["Preflop", "Flop", "Turn", "River"]
    assert rules["btnFirstPostflop"] is False
