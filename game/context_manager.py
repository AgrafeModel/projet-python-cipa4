import json

from openrouter import dataclass

# Main context manager for the game
# Manages both global and per-agent contexts
class GameContextManager:
    def __init__(self):
        self.global_context = []
        self.agent_contexts = {}
        self.contextelementscounter = 0
        self.player_roles = {}  # Store player roles for context filtering

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
        # Concatenate all content for the player with formatting
        formatted_context = []
        for elem in context_elements:
            content = elem["content"]
            if isinstance(content, dict):
                formatted_context.append(f"[{content.get('type', 'info').upper()}] {content.get('content', str(content))}")
            else:
                formatted_context.append(str(content))
        return "\n".join(formatted_context)

    ## Get the full global context
    def get_global_context(self):
        formatted_context = []
        for elem in self.global_context:
            content = elem["content"]
            if isinstance(content, dict):
                formatted_context.append(f"[{content.get('type', 'info').upper()}] {content.get('content', str(content))}")
            else:
                formatted_context.append(str(content))
        return "\n".join(formatted_context)



    # Get the full context for a specific player,
    # interleaving global and player-specific context elements
    def get_full_global_player_context(self, player_name):
        player_context = self.agent_contexts.get(player_name, [])
        global_context = self.global_context

        # Format helper function
        def format_content(content):
            if isinstance(content, dict):
                content_type = content.get('type', 'info').upper()
                content_text = content.get('content', str(content))
                return f"[{content_type}] {content_text}"
            return str(content)

        res = []
        pPtr = 0

        for i in range(len(global_context)):
            global_context_element = global_context[i]
            next_global_id = global_context[i+1]["id"] if i + 1 < len(global_context) else float('inf')

            # Add global context element
            res.append(format_content(global_context_element["content"]))

            # Skip night action details for non-wolves (they shouldn't know what happens at night)
            if isinstance(global_context_element["content"], dict):
                content_text = global_context_element["content"].get("content", "")
                content_type = global_context_element["content"].get("type", "")

                # Non-wolves don't see detailed night actions, only the results in the morning
                if content_type in ["night_action", "wolf_discussion"] and not self._is_wolf(player_name):
                    continue

            # Get all player context elements until the id of the next global context
            while pPtr < len(player_context):
                player_context_element = player_context[pPtr]
                if player_context_element["id"] > next_global_id:
                    break
                res.append(format_content(player_context_element["content"]))
                pPtr += 1

        # Append any remaining player context elements
        while pPtr < len(player_context):
            player_context_element = player_context[pPtr]
            res.append(format_content(player_context_element["content"]))
            pPtr += 1

        return "\n".join(res)


    def increment_counter(self):
        self.contextelementscounter += 1

    def set_player_role(self, player_name, role):
        """Set the role of a player for context filtering"""
        self.player_roles[player_name] = role

    def _is_wolf(self, player_name):
        """Check if a player is a wolf"""
        return self.player_roles.get(player_name, "") == "loup"


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
