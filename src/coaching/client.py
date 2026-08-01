import requests

class OllamaClient:
    """
    Thin wrapper around a local Ollama server's /api/chat endpoint.
    Ollama must be running (`ollama serve`) with the target model pulled
    (`ollama pull llama3.2:3b`) for this to work.
    """
    
    def __init__(self, model: str, host: str = "http://localhost:11434", timeout: float = 20.0):
        self.model = model
        self.host = host.rstrip("/")
        self.timeout = timeout
        
    def chat(self, system: str, user: str) -> str:
        """
        Send a chat request to the Ollama server and return the response text.
        """
        resp = requests.post(
            f"{self.host}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                "stream": False,
                "options": {"temperature": 0.4, "num_predictions": 80},
                },
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"].strip()