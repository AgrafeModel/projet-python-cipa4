from ai.client import OpenRouterClient
from game.context_manager import GameContextManager


class Agent:
    def __init__(self, name,role):
        self.name = name
        self.role = role
        self.alive = True

    # Agent plays its turn using the OpenRouterClient and the given context
    def play(self,client:OpenRouterClient,context:GameContextManager):
        if not self.alive:
            raise Exception(f"Agent {self.name} is dead and cannot play.")

        # load the master prompt txt
        master_prompt = ""
        with open("data/ai_master_prompt.txt", "r", encoding="utf-8") as f:
            master_prompt = f.read()


        player_context= context.get_player_context(self.name)
        messages = [
            {"role": "system", "content": master_prompt},
            {"role": "user", "content": f"Your name is {self.name} and your role is {self.role}. Based on your context: {player_context}, make your move."}
        ]
        response = client.chat_completion_player(messages, max_tokens=150)
        return response
