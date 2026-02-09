from openai import OpenAI
from dataclasses import dataclass
import json

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



    # Method for streaming chat completion using the OpenRouter API
    # This method yields chunks of text as they are received
    # from the API
    # Parameters:
    # - messages: List of message dicts for the chat completion
    # - max_tokens: Maximum number of tokens to generate
    # - temperature: Sampling temperature for generation
    # - on_chunk: Optional callback function to handle each chunk of text
    def chat_completion_stream(self, messages, max_tokens=512, temperature=0.7, on_chunk=None):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        buffer = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content') and delta.content is not None:
                buffer += delta.content
                if on_chunk:
                    on_chunk(delta.content)
        return buffer



    # Method for chat completion using the OpenRouter API
    def chat_completion_player(self, messages, max_tokens=512, temperature=0.7) :
        responseraw = self.client.chat.completions.create(
            model=self.model,
            messages=messages,

            temperature=temperature,

        )

        response_text = responseraw.choices[0].message.content
        if response_text is None:
            raise ValueError("Received empty response from the API")
        formated_response = parse_response(response_text)
        return formated_response


@dataclass
class ResponseFormat:
    action: str
    reasoning: str
    dialogue: str
    cible:str

def parse_response(response_text: str) -> ResponseFormat:
    try:
        ## if formated as markdown : ```json ... ```


        if response_text.startswith("```json"):
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_text = response_text[start:end]
            data = json.loads(json_text)
        else:
            data = json.loads(response_text)


        dialogue = data["dialogue"] if "dialogue" in data else ""
        cible = data["cible"] if "cible" in data else ""
        return ResponseFormat(
            action=data["action"],
            reasoning=data["reasoning"],
            dialogue= dialogue,
            cible= cible,
        )
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Failed to parse response: {e}. Response text: {response_text}")
