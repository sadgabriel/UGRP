import os
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = os.getenv("OPENAI_API_KEY")

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


async def generate_preparation_outputs(system_prompt, preparation_prompts):
    tasks = []

    for prompt in preparation_prompts:
        tasks.append(unstructured_data_generate(system_prompt, prompt))

    preparation_outputs = await asyncio.gather(*tasks)
    return preparation_outputs


async def unstructured_data_generate(system: str, param: str) -> str:
    if not API_KEY:
        raise ValueError("OpenAI API key is not set in environment variables.")

    async with aiohttp.ClientSession(headers=headers) as session:
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": param},
            ],
            "max_tokens": 16384,
        }

        async with session.post(API_URL, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"Error: {response.status}, {await response.text()}")
