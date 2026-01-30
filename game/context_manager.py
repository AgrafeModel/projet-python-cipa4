import json

from openrouter import dataclass

# Main context manager for the game
# Manages both global and per-agent contexts
class GameContextManager:
    def __init__(self):
        self.global_context = []
        self.agent_contexts = {}
        self.contextelementscounter = 0

    ## Add a global context element
    def add_global_context(self,content):
        context_element = {
            "id": self.contextelementscounter,
            "content": content
        }
        self.global_context.append(context_element)
        self.increment_counter()

    ## Add a context element for a specific player
    def add_player_context(self,player_name,content):
        if player_name not in self.agent_contexts:
            self.agent_contexts[player_name] = []
        context_element = {
            "id": self.contextelementscounter,
            "player_name": player_name,
            "content": content
        }
        self.agent_contexts[player_name].append(context_element)
        self.increment_counter()

    ## Get the full context for a specific player
    def get_player_context(self,player_name):
        if player_name not in self.agent_contexts:
            return ""
        context_elements = self.agent_contexts[player_name]
        # Concatenate all content for the player
        return "\n".join([elem["content"] for elem in context_elements])

    ## Get the full global context
    def get_global_context(self):
        return "\n".join([elem["content"] for elem in self.global_context])



    # Get the full context for a specific player,
    # interleaving global and player-specific context elements
    def get_full_global_player_context(self, player_name):
        player_context = self.agent_contexts.get(player_name, [])
        global_context = self.global_context

        res = ""
        pPtr = 0
        for i in range(len(global_context)):
            global_context_element = global_context[i]
            next_global_id = global_context[i+1] if i + 1 < len(global_context) else {"id": float('inf')}
            res += str(global_context_element["content"])
            if("Période:Nuit" in global_context_element["content"]):
                while True:
                    # skip until the next période:nuit
                    next_global_id = global_context[i+1] if i + 1 < len(global_context) else {"id": float('inf')}
                    if("Période:Jour" in global_context_element["content"]):
                        break

            # Get all player context elements until the id of the next global context
            while pPtr < len(player_context):
                player_context_element = player_context[pPtr]
                if player_context_element["id"] > next_global_id["id"]:
                    break
                res += str(player_context_element["content"])
                pPtr += 1

        # Append any remaining player context elements
        while pPtr < len(player_context):
            player_context_element = player_context[pPtr]
            res += str(player_context_element["content"])
            pPtr += 1

        return res


    def increment_counter(self):
        self.contextelementscounter += 1


# Keep track of elements perceive by a specific agent
# for example, the thoughts or memories of an agent
@dataclass
class PlayerContextElement:
    id: int
    player_name: str
    content: str


# Keep track of elements perceive by all agents
# For example, when a player say something aloud
@dataclass
class GlobalContextElements:
    id: int
    content: str
