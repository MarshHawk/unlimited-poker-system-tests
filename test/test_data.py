from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ActivePlayer:
    id: str
    bet: str
    stack: str
    isInactive: bool
    isBigBlind: bool


@dataclass
class StreetEvent:
    streetType: str
    currentActivePlayers: List[ActivePlayer]
    pot: str


@dataclass
class PlayerEvent:
    playerId: str
    action: str
    amount: str
    streetType: str
    currentStack: str
    currentPot: str


@dataclass
class MutationData:
    mutationType: str
    handId: str
    streetEvent: StreetEvent
    playerEvent: PlayerEvent
    cards: Optional[str]


import json
from dataclasses import asdict

# Create instances of ActivePlayer
active_players = [
    ActivePlayer(id="player_one", bet="10", stack="990", isInactive=False, isBigBlind=False),
    ActivePlayer(id="player_two", bet="20", stack="980", isInactive=False, isBigBlind=True),
    ActivePlayer(id="player_three", bet="0", stack="1000", isInactive=True, isBigBlind=False),
]

# Create an instance of StreetEvent
street_event = StreetEvent(streetType="Preflop", currentActivePlayers=active_players, pot="30")

# Create an instance of PlayerEvent
player_event = PlayerEvent(
    playerId="player_three",
    action="Fold",
    amount="0",
    streetType="Preflop",
    currentStack="1000",
    currentPot="30",
)

# Create an instance of MutationData
mutation_data = MutationData(
    mutationType="UPDATED",
    handId="22",
    streetEvent=street_event,
    playerEvent=player_event,
    cards=None,
)

mutation_data_dict = asdict(mutation_data)

# Convert the dictionary to a JSON string
mutation_data_json = json.dumps(mutation_data_dict)


def hand_event_1(hand_id):
    return {
        "data": {
            "handEvent": {
                "mutationType": "UPDATED",
                "handId": hand_id,
                "tableConfig": {
                    "smallBlind": "10",
                    "bigBlind": "20",
                    "buttonIndex": 2,
                },
                "buttonIndex": 2,
                "smallBlindIndex": 0,
                "bigBlindIndex": 1,
                "streetEvent": {
                    "streetType": "Preflop",
                    "currentActivePlayers": [
                        {
                            "id": "player_three",
                            "bet": "0",
                            "stack": "1000",
                            "isInactive": True,
                            "isBigBlind": False,
                        },
                        {
                            "id": "player_one",
                            "bet": "10",
                            "stack": "990",
                            "isInactive": False,
                            "isBigBlind": False,
                        },
                        {
                            "id": "player_two",
                            "bet": "20",
                            "stack": "980",
                            "isInactive": False,
                            "isBigBlind": True,
                        },
                    ],
                    "pot": "30",
                },
                "playerEvent": {
                    "playerId": "player_three",
                    "action": "Fold",
                    "amount": "0",
                    "streetType": "Preflop",
                    "currentStack": "1000",
                    "currentPot": "30",
                },
                "cards": None,
            }
        }
    }


def hand_event_2(hand_id):
    return {
        "type": "data",
        "id": hand_id,
        "payload": {
            "data": {
                "handEvent": {
                    "mutationType": "UPDATED",
                    "handId": hand_id,
                    "tableConfig": {
                        "smallBlind": "10",
                        "bigBlind": "20",
                        "buttonIndex": 2,
                    },
                    "buttonIndex": 2,
                    "smallBlindIndex": 0,
                    "bigBlindIndex": 1,
                    "streetEvent": {
                        "streetType": "Preflop",
                        "currentActivePlayers": [
                            {
                                "id": "player_three",
                                "bet": "0",
                                "stack": "1000",
                                "isInactive": True,
                                "isBigBlind": False,
                            },
                            {
                                "id": "player_one",
                                "bet": "10",
                                "stack": "990",
                                "isInactive": True,
                                "isBigBlind": False,
                            },
                            {
                                "id": "player_two",
                                "bet": "20",
                                "stack": "980",
                                "isInactive": False,
                                "isBigBlind": True,
                            },
                        ],
                        "pot": "30",
                    },
                    "playerEvent": {
                        "playerId": "player_one",
                        "action": "Fold",
                        "amount": "0",
                        "streetType": "Preflop",
                        "currentStack": "990",
                        "currentPot": "30",
                    },
                    "cards": None,
                    "isComplete": True,
                    "winnerId": "player_two",
                }
            }
        },
    }
