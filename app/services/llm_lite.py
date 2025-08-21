"""
Lightweight LLM service for Google Generative AI.
Removes heavy langchain dependencies for smaller deployment.
"""
import requests
import json
from typing import List, Dict, Any, Optional
from app.core.config import GOOGLE_API_KEY

class LightweightGoogleLLM:
    """Lightweight Google LLM client that doesn't depend on langchain."""
    
    def __init__(self, model: str = "gemini-1.5-flash", temperature: float = 0.2):
        self.model = model
        self.temperature = temperature
        self.api_key = GOOGLE_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text response from the model."""
        url = f"{self.base_url}/models/{self.model}:generateContent"
        params = {"key": self.api_key}
        
        # Prepare the request
        contents = []
        
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": system_prompt}]
            })
        
        contents.append({
            "role": "user", 
            "parts": [{"text": prompt}]
        })
        
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperature,
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 2048
            }
        }
        
        response = requests.post(
            url,
            params=params,
            headers={"Content-Type": "application/json"},
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate:
                    parts = candidate["content"]["parts"]
                    return parts[0]["text"] if parts else ""
            return "No response generated"
        else:
            raise Exception(f"LLM API error: {response.status_code} - {response.text}")

# Global instance
llm = LightweightGoogleLLM()
