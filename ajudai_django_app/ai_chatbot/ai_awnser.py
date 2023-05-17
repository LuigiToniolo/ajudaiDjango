import openai
import tiktoken

from get_secret_variables import get_secret_var

openai.api_key = get_secret_var("OPENAI_API_KEY")

def generate_gpt_response(context):
    #TODO
    pass