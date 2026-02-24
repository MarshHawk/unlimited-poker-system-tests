"""
REST API system tests for the Unlimited Poker Go API.
These tests use the REST endpoints instead of GraphQL subscriptions.
"""

import pytest
import requests

BASE_URL = "http://localhost:3000"
HTTP_TIMEOUT_SECONDS = 5

_requests_post = requests.post
_requests_get = requests.get


def _post_with_timeout(*args, **kwargs):
    kwargs.setdefault("timeout", HTTP_TIMEOUT_SECONDS)
    return _requests_post(*args, **kwargs)


def _get_with_timeout(*args, **kwargs):
    kwargs.setdefault("timeout", HTTP_TIMEOUT_SECONDS)
    return _requests_get(*args, **kwargs)


requests.post = _post_with_timeout
requests.get = _get_with_timeout


def test_health_check():
    """Test the health check endpoint."""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "Unlimited Poker API"


def test_deal_creates_hand():
    """Test dealing a new hand."""
    response = requests.post(
        f"{BASE_URL}/api/deal",
        json={
            "tableId": "test-table",
            "players": [
                {"id": "alice", "stack": "1000"},
                {"id": "bob", "stack": "1000"},
                {"id": "charlie", "stack": "1000"},
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "hand" in data
    hand = data["hand"]
    assert hand["tableId"] == "test-table"
    assert len(hand["players"]) == 3
    assert len(hand["cards"]["flop"]) == 3
    assert hand["cards"]["turn"] != ""
    assert hand["cards"]["river"] != ""


def test_deal_requires_minimum_players():
    """Test that dealing requires at least 2 players."""
    response = requests.post(
        f"{BASE_URL}/api/deal",
        json={
            "tableId": "test-table",
            "players": [{"id": "alice", "stack": "1000"}],
        },
    )
    assert response.status_code == 400
    assert "error" in response.json()


def test_list_hands():
    """Test listing all hands."""
    # First deal a hand
    requests.post(
        f"{BASE_URL}/api/deal",
        json={
            "tableId": "list-test",
            "players": [
                {"id": "alice", "stack": "1000"},
                {"id": "bob", "stack": "1000"},
            ],
        },
    )

    response = requests.get(f"{BASE_URL}/api/hands")
    assert response.status_code == 200
    data = response.json()
    assert "hands" in data
    assert "count" in data
    assert data["count"] >= 1


def test_get_hand_by_id():
    """Test getting a specific hand."""
    # Deal a hand first
    deal_response = requests.post(
        f"{BASE_URL}/api/deal",
        json={
            "tableId": "get-test",
            "players": [
                {"id": "alice", "stack": "1000"},
                {"id": "bob", "stack": "1000"},
            ],
        },
    )
    hand_id = deal_response.json()["id"]

    response = requests.get(f"{BASE_URL}/api/hands/{hand_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == hand_id


def test_get_nonexistent_hand():
    """Test getting a hand that doesn't exist."""
    response = requests.get(f"{BASE_URL}/api/hands/nonexistent-id")
    assert response.status_code == 404


def test_play_turn_bet():
    """Test playing a bet action."""
    # Deal a hand
    deal_response = requests.post(
        f"{BASE_URL}/api/deal",
        json={
            "tableId": "play-test",
            "players": [
                {"id": "alice", "stack": "1000"},
                {"id": "bob", "stack": "1000"},
                {"id": "charlie", "stack": "1000"},
            ],
        },
    )
    hand_id = deal_response.json()["id"]

    # Charlie calls 20 (UTG)
    response = requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={
            "handId": hand_id,
            "playerId": "charlie",
            "action": "Bet",
            "amount": "20",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["gameOver"] == False
    assert data["hand"]["id"] == hand_id


def test_play_turn_fold():
    """Test playing a fold action."""
    # Deal a hand
    deal_response = requests.post(
        f"{BASE_URL}/api/deal",
        json={
            "tableId": "fold-test",
            "players": [
                {"id": "alice", "stack": "1000"},
                {"id": "bob", "stack": "1000"},
                {"id": "charlie", "stack": "1000"},
            ],
        },
    )
    hand_id = deal_response.json()["id"]

    # Charlie folds
    response = requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={
            "handId": hand_id,
            "playerId": "charlie",
            "action": "Fold",
            "amount": "0",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["gameOver"] == False  # Still 2 players left


def test_last_player_wins():
    """Test that the last remaining player wins."""
    # Deal a hand
    deal_response = requests.post(
        f"{BASE_URL}/api/deal",
        json={
            "tableId": "win-test",
            "players": [
                {"id": "alice", "stack": "1000"},
                {"id": "bob", "stack": "1000"},
                {"id": "charlie", "stack": "1000"},
            ],
        },
    )
    hand_id = deal_response.json()["id"]

    # Charlie folds
    requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={
            "handId": hand_id,
            "playerId": "charlie",
            "action": "Fold",
            "amount": "0",
        },
    )

    # Alice folds - Bob wins
    response = requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={
            "handId": hand_id,
            "playerId": "alice",
            "action": "Fold",
            "amount": "0",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["gameOver"] == True
    assert data["winner"] == "bob"


def test_complete_betting_round():
    """Test a complete preflop betting round transitioning to flop."""
    # Deal a hand
    deal_response = requests.post(
        f"{BASE_URL}/api/deal",
        json={
            "tableId": "round-test",
            "players": [
                {"id": "alice", "stack": "1000"},
                {"id": "bob", "stack": "1000"},
                {"id": "charlie", "stack": "1000"},
            ],
        },
    )
    hand_id = deal_response.json()["id"]

    # Charlie calls 20
    requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={
            "handId": hand_id,
            "playerId": "charlie",
            "action": "Bet",
            "amount": "20",
        },
    )

    # Alice calls 10 (already has 10 as SB)
    requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={
            "handId": hand_id,
            "playerId": "alice",
            "action": "Bet",
            "amount": "10",
        },
    )

    # Bob checks (already has 20 as BB) - should move to flop
    response = requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={
            "handId": hand_id,
            "playerId": "bob",
            "action": "Check",
            "amount": "0",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["gameOver"] == False

    # Check that we moved to flop
    hand = data["hand"]
    last_street = hand["streetEvents"][-1]
    assert last_street["streetType"] == "Flop"
    assert last_street["pot"] == "60"  # 20 + 20 + 20


def test_full_game_to_showdown():
    """Test playing a complete game to showdown."""
    # Deal a 2-player hand
    deal_response = requests.post(
        f"{BASE_URL}/api/deal",
        json={
            "tableId": "showdown-test",
            "players": [
                {"id": "alice", "stack": "1000"},
                {"id": "bob", "stack": "1000"},
            ],
        },
    )
    hand_id = deal_response.json()["id"]

    # Preflop: Alice calls 10, Bob checks
    requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={"handId": hand_id, "playerId": "alice", "action": "Bet", "amount": "10"},
    )
    requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={"handId": hand_id, "playerId": "bob", "action": "Check", "amount": "0"},
    )

    # Flop (heads-up postflop): BB acts first, then SB
    requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={"handId": hand_id, "playerId": "bob", "action": "Check", "amount": "0"},
    )
    requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={"handId": hand_id, "playerId": "alice", "action": "Check", "amount": "0"},
    )

    # Turn: BB acts first, then SB
    requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={"handId": hand_id, "playerId": "bob", "action": "Check", "amount": "0"},
    )
    requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={"handId": hand_id, "playerId": "alice", "action": "Check", "amount": "0"},
    )

    # River: BB acts first, then SB (final action) - game should end
    requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={"handId": hand_id, "playerId": "bob", "action": "Check", "amount": "0"},
    )
    response = requests.post(
        f"{BASE_URL}/api/hands/{hand_id}/play",
        json={"handId": hand_id, "playerId": "alice", "action": "Check", "amount": "0"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["gameOver"] == True
    assert data["winner"] in ["alice", "bob"]
    assert data["hand"]["isComplete"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
