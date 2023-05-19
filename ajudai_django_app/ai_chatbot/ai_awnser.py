import openai
from ajudai_django_app.ai_chatbot.ai_tools import count_tokens, instruction_builder, messages_to_string
from constants import AWNSER_WHEN_MESSAGE_IS_OVER_THE_LIMIT, CHAT_API_GENERAL_ERROR_MESSAGE, MIN_TOKEN_LIMIT_RATE_LEFT_TO_AWNSER

from get_secret_variables import get_secret_var

openai.api_key = get_secret_var("OPENAI_API_KEY")

def generate_gpt_response(prompt, context, role, aditional_instructions, model_name, model_token_limit):
    instructions = instruction_builder(aditional_instructions, role)
    token_limit = model_token_limit

    #a mínima estrutura para a requisição será a instrução mais o prompt. Caso haja rompimento do máximo pelo contexto passado, ele será elimido até funcionar
    tokens_prompt_and_instructions = count_tokens(model_name, instructions + ' ' + prompt)

    #avaliação de cumprimento do limite de requisição do modelo, sem considerar o context:
    if tokens_prompt_and_instructions > token_limit * (1-MIN_TOKEN_LIMIT_RATE_LEFT_TO_AWNSER):
        awnser = AWNSER_WHEN_MESSAGE_IS_OVER_THE_LIMIT
        context.append({"role": "assistant", "content": awnser})
        tokens_used  = 0
        return awnser, context, tokens_used
    
    else:
        #se for a primeira mensagem, nenhma verificação adicional de respeito de limite precisa ser feita
        if context == []:
            context = [
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt},
                ]
        else:
            #aqui, verifica-se se, com todo o contexto passado existe rompimento de limite. caso sim, será eliminado, até caber no limite, as mensagens da mais antiga a mais nova
            context.append({"role": "user", "content": prompt})
            total_tokens = count_tokens(model_name, messages_to_string(context))
            while total_tokens > token_limit * (1-MIN_TOKEN_LIMIT_RATE_LEFT_TO_AWNSER) and len(context) > 2:
                context.pop(1)
                total_tokens = count_tokens(model_name, messages_to_string(context))
            
        try:    
            completions = openai.ChatCompletion.create(
                model=model_name,
                messages=context
            )

            awnser = completions['choices'][0]['message']['content']
            context.append({"role": "assistant", "content": awnser})
            tokens_used = completions.usage['total_tokens']
        
        except Exception as e:
            awnser = CHAT_API_GENERAL_ERROR_MESSAGE
            tokens_used = 0

    return awnser, context, tokens_used

def pedido_confirmado(resposta):
    if "Pedido Confirmado" in resposta:
        resumo = resposta.split("Pedido Confirmado")[1]
        resumo = " ".join(resumo.split())
        return True, resumo
    
    else: 
        return False, ''