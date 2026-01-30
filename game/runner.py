import json
import os
from ai.client import OpenRouterClient, OpenRouterClientConfig
from game.agent import Agent
from game.context_manager import GameContextManager
import random

class GameRunner:
    def __init__(self,player_count) -> None:
        self.roles = [
            "Villageois",
            "Loup-Garou",
            "Voyante",
            "Chasseur",
            "Sorcière",
        ]

        key = os.getenv("OPENROUTER_API_KEY")
        if key is None:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.player_count = player_count
        self.agents: list[Agent] = []
        self.context_manager = GameContextManager()
        self.client = OpenRouterClient(OpenRouterClientConfig(key))
        self.current_turn = 0
        # start at night
        self.periode = 2

        self.context_manager.add_global_context("Période: Nuit")

        with open("data/ai_names.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        self.ai_names = data["prenoms"]

        for i in range(player_count):
            name = self.ai_names[random.randint(0,60)]
            role = self.roles[i % len(self.roles)]
            agent = Agent(name, role)
            self.agents.append(agent)

        print("Joueurs dans la partie:")
        for agent in self.agents:
            print(agent.name)

    def get_players_alive(self):
        r = []
        for p in self.agents:
            if p.alive:
                r.append(p)
        return r

    # période suivante: jour, vote, nuit, jour, vote ...
    def next_periode(self):
        self.periode = (self.periode + 1) % 3
        self.context_manager.add_global_context("Période:"+self.periode_text())

    def periode_text(self):
        if self.periode == 0:
            return "JourDiscussion"
        elif self.periode == 1:
            return "Vote"
        else:
            return "Nuit"

    def play_periode(self):
        for i in range(6 if self.periode == 0 else 1):
            # a list of id for the turn order randomly
            turn_order = [i for i in range(len(self.agents)) if self.agents[i].alive]
            random.shuffle(turn_order)
            for i in turn_order:
                agent = self.agents[i]
                if agent.alive:
                    print("--------------------")
                    print(f"Turn {self.current_turn+1}: {agent.name} ({agent.role}) is playing.")
                    current_play =agent.play(self.periode_text(),self.client,self.context_manager)
                    match current_play.action:
                        case "éliminer":
                            # set the player dead
                            for agent in self.agents:
                                if agent.name == current_play.cible:
                                    agent.alive = False

                    print("action:\n",current_play.action)
                    print("dialogue:\n",current_play.dialogue)
                    if current_play.cible != "":
                        print("cible: ",current_play.cible)

            self.current_turn += 1
