from ai.ollama_client import OllamaClient

client = OllamaClient()
print(client.list_models())
print(client.generate("Dis bonjour en français").response)