from dotenv import load_dotenv
import os
from openai import OpenAI
from openrouter import dataclass
load_dotenv()


@dataclass
class OpenRouterClientConfig:
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    model: str = "openai/gpt-oss-20b:free"


# Main client class for OpenRouter API interactions
class OpenRouterClient:
    def __init__(self, config: OpenRouterClientConfig):
        self.client = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
        )
        self.model = config.model

    def load_master_prompt(self, file_path):
           with open(file_path, "r", encoding="utf-8") as file:
               return file.read()



    # Method for chat completion using the OpenRouter API
    def chat_completion_player(self, messages, max_tokens=512, temperature=0.7) :

        master_prompt = self.load_master_prompt("prompts/master.txt")

        # Add the master prompt as a system message
        system_message = {"role": "system", "content": master_prompt}
        messages.insert(0, system_message)


        responseraw = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )


        response_text = responseraw.choices[0].message.content
        if response_text is None:
            raise ValueError("Received empty response from the API")
        formated_response = parse_response(response_text)
        return formated_response



@dataclass
class ResponseFormat:
    role: str
    action: str
    reasoning: str
    dialogue: str

def parse_response(response_text: str) -> ResponseFormat:
    import json
    data = json.loads(response_text)
    return ResponseFormat(
        role=data["role"],
        action=data["action"],
        reasoning=data["reasoning"],
        dialogue=data["dialogue"]
    )


# Configuration du client
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key is None:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set")
config = OpenRouterClientConfig(api_key=api_key)
client = OpenRouterClient(config)

# Messages pour le contexte du jeu
messages = [
{"role": "user", "content": "Tu es un Loup-Garou. Comment comptes-tu convaincre les autres que tu es innocent ?"},
]

# Appel à l'API
response = client.chat_completion_player(messages)
print(response)
