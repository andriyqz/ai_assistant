import asyncio
import aiohttp

class Perplexity:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_response(self, messages: list):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        json_data = {
            'model': 'sonar-pro',
            'messages': messages
        }

        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.perplexity.ai/chat/completions',
                                    headers=headers,
                                    json=json_data) as response:
                response = await response.json()
 
                return response['choices'][0]['message']['content']