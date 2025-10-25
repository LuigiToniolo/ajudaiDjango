from openai import OpenAI
from get_secret_variables import get_secret_var

_client = None


def get_openai_client():
    global _client
    if _client is None:
        api_key = get_secret_var("OPENAI_API_KEY")
        _client = OpenAI(api_key=api_key)
    return _client


