import json

from openrouter import dataclass

# Main context manager for the game
# Manages both global and per-agent contexts
class GameContextManager:
    def __init__(self):
        self.global_context = []
        self.agent_contexts = {}
        self.contextelementscounter = 0

    def get_player_context(self,player_name):
        raise NotImplementedError("Method get_player_context is not implemented yet.")

    def addToPlayerContext(self,player_name,context_element):
        raise NotImplementedError("Method addToPlayerContext is not implemented yet.")





# Keep track of elements perceive by a single agent
@dataclass
class PlayerContextElement:
    id: int
    player_name: str
    content: str


# Keep track of elements perceive by all agents
@dataclass
class GlobalContextElements:
    id: int
    content: str
