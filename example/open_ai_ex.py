import openai
from loguru import logger

from api_multikey.exception import APIKeyError
from api_multikey.multikey import with_key_from_storage, init_key_to_storage


@with_key_from_storage()
def ask(api_key: str, prompt: str):
    try:
        model_id = 'gpt-3.5-turbo'
        openai.api_key = api_key

        conversation = [{'role': 'user', 'content': prompt}]
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=conversation
        )
        logger.info(f"Use API_KEY: {api_key}")
        logger.info(f"{prompt}\n{response.choices[0].message.content}")
        return response
    except openai.error.RateLimitError:
        raise APIKeyError


init_key_to_storage(keys=[
    "your_api_key_1",
    "your_api_key_2",
    " ... etc ..."
])
text = []
for _ in range(10):
    ask(prompt=f"Test Hi {_}")
