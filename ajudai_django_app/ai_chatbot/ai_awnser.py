import openai
from ajudai_django_app.ai_chatbot.ai_tools import count_tokens, instruction_builder, messages_to_string
from constants import AWNSER_WHEN_MESSAGE_IS_OVER_THE_LIMIT, CHAT_API_GENERAL_ERROR_MESSAGE, CHAT_API_MESSAGE_AND_AWNSER_OVERLIMT_EVEN_TRYING_TO_SHORT, MIN_TOKEN_LIMIT_RATE_LEFT_TO_AWNSER, TOKEN_LIMIT_MARGIN

from get_secret_variables import get_secret_var

openai.api_key = get_secret_var("OPENAI_API_KEY")

def generate_gpt_response(prompt, context, role, aditional_instructions, model_name, model_token_limit):
    instructions = instruction_builder(aditional_instructions, role)
    token_limit = model_token_limit

    #a mínima estrutura para a requisição será a instrução mais o prompt. Caso haja rompimento do máximo pelo contexto passado, ele será elimido até funcionar
    tokens_prompt_and_instructions = count_tokens(model_name, instructions + ' ' + prompt)

    possivel_obter_resposta = True
    
    #avaliação de cumprimento do limite de requisição do modelo, sem considerar o context:
    if (tokens_prompt_and_instructions*(1+TOKEN_LIMIT_MARGIN)) > token_limit * (1-MIN_TOKEN_LIMIT_RATE_LEFT_TO_AWNSER):
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
            total_tokens = count_tokens(model_name, messages_to_string(context))*(1+TOKEN_LIMIT_MARGIN)
            while total_tokens > (token_limit * (1-MIN_TOKEN_LIMIT_RATE_LEFT_TO_AWNSER)) and len(context) > 2:
                context.pop(1)
                total_tokens = count_tokens(model_name, messages_to_string(context))*(1+TOKEN_LIMIT_MARGIN)
            #AQUI, MESMO TENDO DEIXADO O CONMTEXT APENAS COM DUAS MENSAGENS (O SYSTEM E A ULTIMA PERGUNTA, AINDA NÃO FOI POSSÍVEL CHEGAR AO LIMITE)
            if  total_tokens > (token_limit * (1-MIN_TOKEN_LIMIT_RATE_LEFT_TO_AWNSER)):
                #retira-se a pergunta que é impossível de se fazer e, na awnser devolvida, que sequer estará em context, informa para refazer a pergunta
                awnser = CHAT_API_MESSAGE_AND_AWNSER_OVERLIMT_EVEN_TRYING_TO_SHORT
                context.pop(1)
                tokens_used = 0
                possivel_obter_resposta = False
            else:
                possivel_obter_resposta = True
            
        if possivel_obter_resposta:
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
    elif "Pedido confirmado" in resposta:
        resumo = resposta.split("Pedido confirmado")[1]
    elif "pedido confirmado" in resposta:
        resumo = resposta.split("pedido confirmado")[1]
    else: 
        return False, ''
    
    resumo = " ".join(resumo.split())
    return True, resumo