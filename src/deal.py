import requests

HTTP_TIMEOUT_SECONDS = 5

deal_subscription = """
subscription DealSubscription($mutationType: MutationType) {
  deal(mutationType: $mutationType) {
    mutationType
    id
    deal {
      id
      tableId
      players {
        id
        stack
        cards
        score
        description
      }
      cards {
        flop
        turn
        river
      }
      playerEvents {
        playerId
        action
        amount
        streetType
        currentStack
        currentPot
      }
      streetEvents {
        streetType
        currentActivePlayers {
          id
          bet
          stack
          isInactive
        }
        pot
      }
    }
  }
}
"""

deal_subscription_header = {"X-User-Token": "sean", "X-Table-Token": "123"}

deal_mutation_query = """
mutation DealHand($dealInput: DealInput!) {
    deal(dealInput: $dealInput)
}
"""


def deal_mutation_params(players, stacks=None):
    if stacks is None:
        stacks = {p: 1000.0 for p in players}
    return {
        "dealInput": {
            "players": [{"id": p, "stack": stacks.get(p, 1000.0)} for p in players],
            "tableId": "123",
        }
    }


deal_mutation_headers = {"X-User-Token": "", "X-Table-Token": ""}


def execute_deal_mutation(players, stacks=None):
    deal = requests.post(
        "http://localhost:3000/graphql",
        json={
            "query": deal_mutation_query,
            "variables": deal_mutation_params(players, stacks),
        },
        headers=deal_mutation_headers,
        timeout=HTTP_TIMEOUT_SECONDS,
    )
    return deal.json()


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
