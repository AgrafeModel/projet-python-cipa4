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
        messages = [
            {"role": "system", "content": master_prompt},
            {"role": "user", "content": f"Ton nom est {self.name} et ton rôle est {self.role}. Basé sur ton context: {player_context}, que fais-tu ?"},
            {"role": "user", "content": f"La période actuelle est : {periode}."}
        ]
        response = client.chat_completion_player(messages, max_tokens=150)

        global_context_content = {
            "agent": self.name,
            "action":response.action,
            "dialogue":response.dialogue,
        }

        player_context_content = {
            "reasoning":response.reasoning,
        }

        context.add_global_context(global_context_content)
        context.add_player_context(self.name,player_context_content)

        return response
