import openai
import tiktoken
from constants import AI_PROVIDER_OPEN_AI, MAX_INSTRUCTIONS_RATE_SIZE

from get_secret_variables import get_secret_var

openai.api_key = get_secret_var("OPENAI_API_KEY")

def count_tokens(model, content):
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(content))

def instructions_token_limits(model_tokens_limits):
    return int(model_tokens_limits * MAX_INSTRUCTIONS_RATE_SIZE)

def instructions_under_the_limits(instructions, model_name, model_tokens_limits):
    instructions_tokens = count_tokens(model_name, instructions)
    if instructions_tokens <= instructions_token_limits(model_tokens_limits):
        return True
    return False

def instructions_over_limit_error_messages(model, instructions, model_tokens_limits):
    instructions_tokens = count_tokens(model, instructions)

    message = 'As instruções excedem o limite de tokens para o nível de capacidade do chatbot. O limite é' + str(instructions_token_limits(model_tokens_limits))  + ' tokens e as suas instruções possuem' + str(instructions_tokens) + ' tokens.'

    return message

def instruction_builder(aditional_instruction = '', role = ''):
    intro = ''

    instructions = intro + ' ' + role + ' ' + aditional_instruction
    
    return instructions

def messages_to_string(messages_context):
    return ' '.join([message["content"] for message in messages_context])