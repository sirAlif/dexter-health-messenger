import openai
from config.conf import Config

# Load environment variables
conf = Config()


class OpenAIService:
    def __init__(self):
        openai.api_key = conf.OPENAI_API_KEY

    async def send_prompt_to_gpt(self, prompt: str) -> str:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
            )
            return response.choices[0].message["content"]
        except Exception as e:
            raise Exception(f"Failed to connect to OpenAI: {e}")
