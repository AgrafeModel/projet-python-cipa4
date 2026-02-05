from ai.client import OpenRouterClient, parse_response
from game.context_manager import GameContextManager


class Agent:
    def __init__(self, name,role):
        self.name = name
        self.role = role
        self.alive = True

    # Agent plays its turn using the OpenRouterClient and the given context
    def play(self,periode:str,client:OpenRouterClient,context:GameContextManager):
        if not self.alive:
            raise Exception(f"Agent {self.name} is dead and cannot play.")

        # load the master prompt txt
        master_prompt = ""
        with open("prompts/master.txt", "r", encoding="utf-8") as f:
            master_prompt = f.read()

        player_context= context.get_full_global_player_context(self.name)

        print(f"[DEBUG] Agent {self.name} is playing with context:")
        print(f"[DEBUG] Context length: {len(player_context)} characters")
        print(f"[DEBUG] Context content:\n{player_context}")
        print(f"[DEBUG] Context is empty: {not player_context.strip()}")
        print(f"[DEBUG] End of context debug\n")

        messages = [
            {"role": "system", "content": master_prompt},
            {"role": "user", "content": f"Ton nom est {self.name} et ton rôle est {self.role}. Basé sur ton context: {player_context}, que fais-tu ?"},
            {"role": "user", "content": f"La période actuelle est : {periode}."}
        ]

         # get the response from the client
        response = client.chat_completion_player(messages, max_tokens=150)
        print(f"[DEBUG] Raw response from agent {self.name}:\n{response}\n")

        # Add action to global context in a readable format (what others can observe)
        if response.dialogue and response.dialogue.strip():
            global_context_content = {
                "type": "player_action",
                "content": f"{self.name} fait l'action '{response.action}' et dit: \"{response.dialogue}\""
            }
            context.add_global_context(global_context_content)

        # Add private reasoning to player context (internal thoughts)
        player_context_content = {
            "type": "reasoning",
            "content": f"Mon raisonnement: {response.reasoning}"
        }
        context.add_player_context(self.name, player_context_content)

        return response
