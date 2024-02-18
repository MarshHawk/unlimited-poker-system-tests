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

from dataclasses import asdict
import json

# Assume you have an instance of MutationData
mutation_data_instance = MutationData(...)

# Convert the dataclass instance to a dictionary
mutation_data_dict = asdict(mutation_data_instance)

# Convert the dictionary to a JSON string
mutation_data_json = json.dumps(mutation_data_dict)

#print(mutation_data_json)

# Create instances of ActivePlayer
active_players = [
    ActivePlayer(id='player_one', bet='10', stack='990', isInactive=False, isBigBlind=False),
    ActivePlayer(id='player_two', bet='20', stack='980', isInactive=False, isBigBlind=True),
    ActivePlayer(id='player_three', bet='0', stack='1000', isInactive=True, isBigBlind=False)
]

# Create an instance of StreetEvent
street_event = StreetEvent(streetType='PREFLOP', currentActivePlayers=active_players, pot='30')

# Create an instance of PlayerEvent
player_event = PlayerEvent(playerId='player_three', action='FOLD', amount='0', streetType='PREFLOP', currentStack='1000', currentPot='30')

# Create an instance of MutationData
mutation_data = MutationData(mutationType='UPDATED', handId='22', streetEvent=street_event, playerEvent=player_event, cards=None)