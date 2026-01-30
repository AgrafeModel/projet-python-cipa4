from dotenv.main import load_dotenv
from game.runner import GameRunner
# from gui.app import App
load_dotenv()



if __name__ == "__main__":
    game = GameRunner(player_count=5)
    alives = game.get_players_alive()
    while len(alives) > 1:
        game.play_periode()
        game.next_periode()
        alives = game.get_players_alive()
