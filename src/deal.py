import requests

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
    return {
        "dealInput": {
            "players": [
                {"id": players[0], "stack": 1000.0},
                {"id": players[1], "stack": 1000.0},
                {"id": players[2], "stack": 1000.0},
            ],
            "tableId": "123",
        }
    }


deal_mutation_headers = {"X-User-Token": "", "X-Table-Token": ""}

def execute_deal_mutation(players):
    body = {
        "query": deal_mutation_query,
        "variables": deal_mutation_params(players),
    }
    print("body:")
    print(body)
    deal = requests.post(
        "http://localhost:8097/graphql",
        json={
            "query": deal_mutation_query,
            "variables": deal_mutation_params(players),
        },
        headers=deal_mutation_headers,
    )
    print(deal.json())

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
    