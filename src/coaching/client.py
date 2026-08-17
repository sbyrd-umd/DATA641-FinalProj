import requests
import os
from openai import OpenAI

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

class OpenAIClient:
    """
    Thin wrapper around OpenAI's chat completions endpoint.
    Requires OPENAI_API_KEY in the environment.
    """

    def __init__(self, model: str = "gpt-4o-mini", timeout: float = 20.0):
        self.model = model
        self.timeout = timeout
        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def chat(self, system: str, user: str) -> str:
        """Send a chat request to OpenAI and return the response text."""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=0.4,
            max_tokens=80,
        )
        return response.choices[0].message.content.strip()