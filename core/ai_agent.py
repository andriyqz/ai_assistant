from core.perplexity import Perplexity
from core.utils import get_config


class AiAgent:
    def __init__(self, api_key: str, start_prompt: str) -> None:
        self.messages = [{'role': 'system', 'content': start_prompt}]
        self._perplexity_ai = Perplexity(api_key=api_key)
        
    async def send_message(self, message: str) -> str:
        self.messages.append({'role': 'user', 'content': message})
        response = await self._perplexity_ai.get_response(messages=self.messages)
        
        self.messages.append({'role': 'assistant', 'content': response})
        
        return response