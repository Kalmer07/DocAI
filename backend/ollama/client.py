"""
Ollama Client - Integration with Local AI
"""
import aiohttp
from typing import List, Optional, Dict, Any
from ollama.models import ModelInfo


class OllamaClient:
    """
    Async client for Ollama API.
    Handles model listing, generation with streaming support.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the client session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def list_models(self) -> List[ModelInfo]:
        """
        Get list of available models from Ollama.
        
        Returns:
            List of ModelInfo objects
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/tags"
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Ollama API error: {response.status}")
                
                data = await response.json()
                models = []
                
                for model_data in data.get("models", []):
                    models.append(ModelInfo(
                        name=model_data.get("name", "unknown"),
                        size=self._format_size(model_data.get("size", 0)),
                        family=model_data.get("details", {}).get("family", "unknown"),
                        modified_at=model_data.get("modified_at", "")
                    ))
                
                return models
        except aiohttp.ClientError as e:
            raise Exception(f"Failed to connect to Ollama: {str(e)}")
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        config: Dict[str, Any] = None,
        stream: bool = False
    ) -> str:
        """
        Generate text using Ollama.
        
        Args:
            system_prompt: System instruction prompt
            user_prompt: User input prompt
            config: Model configuration (model, temperature, etc.)
            stream: Whether to stream the response
            
        Returns:
            Generated text
        """
        config = config or {}
        session = await self._get_session()
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": config.get("model", "llama3.2"),
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": stream,
            "options": {
                "temperature": config.get("temperature", 0.3),
                "top_p": config.get("top_p", 0.9),
                "num_ctx": config.get("context_size", 4096),
            }
        }
        
        if config.get("seed") is not None:
            payload["options"]["seed"] = config["seed"]
        
        try:
            if stream:
                return await self._generate_stream(session, url, payload)
            else:
                return await self._generate_single(session, url, payload)
        except aiohttp.ClientError as e:
            raise Exception(f"Ollama generation failed: {str(e)}")
    
    async def _generate_single(
        self,
        session: aiohttp.ClientSession,
        url: str,
        payload: Dict
    ) -> str:
        """Non-streaming generation"""
        async with session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Ollama error: {error_text}")
            
            data = await response.json()
            return data.get("response", "")
    
    async def _generate_stream(
        self,
        session: aiohttp.ClientSession,
        url: str,
        payload: Dict
    ) -> str:
        """Streaming generation with progress callback"""
        full_response = ""
        
        async with session.post(url, json=payload) as response:
            if response.status != 200:
                raise Exception(f"Ollama streaming error: {response.status}")
            
            # Stream line by line (each line is a JSON object)
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line:
                    try:
                        import json
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        full_response += chunk
                        
                        # Here you could emit progress via WebSocket
                        # yield chunk
                        
                    except json.JSONDecodeError:
                        continue
        
        return full_response
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"


# Global client instance (used by FastAPI lifespan)
_ollama_client: Optional[OllamaClient] = None


def get_client() -> OllamaClient:
    """Get the global Ollama client instance"""
    if _ollama_client is None:
        raise RuntimeError("Ollama client not initialized")
    return _ollama_client
