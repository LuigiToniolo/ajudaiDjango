import openai
import json
from ajudai_django_app.ai_chatbot.ai_extration import ai_gpt_extrair_informacao_do_cardapio
from ajudai_django_app.ai_chatbot.ai_tools import count_tokens, instruction_builder, messages_to_string
from ajudai_django_app.models import ChatBot, Pedido
from constants import AWNSER_WHEN_MESSAGE_IS_OVER_THE_LIMIT, CHAT_API_GENERAL_ERROR_MESSAGE, CHAT_API_MESSAGE_AND_AWNSER_OVERLIMT_EVEN_TRYING_TO_SHORT, MIN_TOKEN_LIMIT_RATE_LEFT_TO_AWNSER, TOKEN_LIMIT_MARGIN

from get_secret_variables import get_secret_var

openai.api_key = get_secret_var("OPENAI_API_KEY")

def obeter_info_produto_cardapio(informacao_solicitada, chatbot_id):
    try:
        chatbot = ChatBot.objects.get(
                    id=chatbot_id,
                    )
        cardapio = chatbot.cardapio
        return ai_gpt_extrair_informacao_do_cardapio(informacao_solicitada, cardapio)
    except:
        return 'Não foi possível extrair informações do cardápio'

def criar_pedido_e_retornar_resumo(
        nome_cliente, 
        endereco_cliente,
        itens_pedido,
        valor_total,
        metodo_de_pagamento,
        user, 
        conversation
    ):
    resumo_do_pedido = f"Seu pedido foi confirmado! \nResumo do Pedido:\n - Nome do Cliente: {nome_cliente} \n - Itens do pedido: {itens_pedido} \n - Total do pedido: {valor_total} \n - Método de Pagamento: {metodo_de_pagamento} - Endereço: {endereco_cliente}"
    try:
        Pedido.criar_novo_pedido_ja_com_parametros(nome_cliente, endereco_cliente, itens_pedido, valor_total, metodo_de_pagamento, resumo_do_pedido, user, conversation)
        return resumo_do_pedido
    except:
        #TODO aqui, caso necessário, pode executar outras funções, como, desativar automaticamnte o chatbot
        return 'Não foi possível realizar o fechamento do pedido. Tente novamente ou aguarde até que um atendente humano assuma a conversa'



def generate_gpt_response(prompt, context, role, aditional_instructions, model_name, model_token_limit, chatbot_id, user, conversation):
    instructions = instruction_builder(aditional_instructions, role)
    token_limit = model_token_limit
    chatbot = ChatBot.objects.get(id=chatbot_id)
    functions = [
        {
            "name": "obeter_info_produto_cardapio",
            "description": chatbot.descricao_funcao_cardapio,
            "parameters": {
                "type": "object",
                "properties": {
                    "informacao_solicitada": {
                        "type": "string",
                        "description": chatbot.descricao_informacao_solicitada_do_cardapio,
                    },
                },
                "required": ["informacao_solicitada"],
            },
        },
        {
            "name": "criar_pedido_e_retornar_resumo",
            "description": 'Realiza a confirmação do pedido e retorna um resumo final do pedido',
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_cliente": {
                        "type": "string",
                        "description": 'Nome do cliente',
                    },
                    "endereco_cliente": {
                        "type": "string",
                        "description": 'Caso a opção seja por entrega, fornecer o Endereço do cliente completo, inclusive com o CEP. Caso a opção seja por retirada no balção, fornecer o endereço do Estbelecimento',
                    },
                    "itens_pedido": {
                        "type": "string",
                        "description": 'Itens do pedido do cliente, cada qual o respectivo preço. Inserir a taxa de entrega como um item caso a opção seja de entrega (e não retirada no balcão) (exemplo: Pizza de Mussarela Grande - R$ 45,00; Cola Cola lata - R$ 5,00; Taxa de Entrega R$ 5,00;)',
                    },
                    "valor_total": {
                        "type": "string",
                        "description": 'Valor total do pedido, ou seja, a soma total dos valores dos itens do pedido. Inserir o preço da taxa de entrega caso a opção seja de entrega (e não retirada no balcão)',
                    },
                    "metodo_de_pagamento": {
                        "type": "string",
                        "description": 'Método de pagamento escolhido pelo cliente (por exemplo: pix)',
                    },
                },
                "required": ["nome_cliente", "endereco_cliente", "itens_pedido"],
            },
        },

    ]

    #a mínima estrutura para a requisição será a instrução mais o prompt. Caso haja rompimento do máximo pelo contexto passado, ele será elimido até funcionar
    tokens_prompt_and_instructions = count_tokens(model_name, instructions + ' ' + prompt)

    possivel_obter_resposta = True
    
    #avaliação de cumprimento do limite de requisição do modelo, sem considerar o context:
    if (tokens_prompt_and_instructions*(1+TOKEN_LIMIT_MARGIN)) > token_limit * (1-MIN_TOKEN_LIMIT_RATE_LEFT_TO_AWNSER):
        awnser = AWNSER_WHEN_MESSAGE_IS_OVER_THE_LIMIT

        #garante que o primeiro prompt de system tenha as instruções mais atualizadas
        context[0] = {"role": "system", "content": instructions}
        
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
            #garante que o primeiro prompt de system tenha as instruções mais atualizadas
            context[0] = {"role": "system", "content": instructions}
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
                    temperature=0,
                    messages=context,
                    functions=functions,
                    function_call="auto",
                )

                response_message = completions["choices"][0]["message"]
                if response_message.get("function_call"):
                    available_functions = {
                        "obeter_info_produto_cardapio": obeter_info_produto_cardapio,
                    } 
                    function_name = response_message["function_call"]["name"]
                    fuction_to_call = available_functions[function_name]
                    function_args = json.loads(response_message["function_call"]["arguments"])
                    if function_name == 'obeter_info_produto_cardapio':
                        function_response = fuction_to_call(
                            informacao_solicitada=function_args.get("informacao_solicitada"),
                            chatbot_id=chatbot_id,
                        )
                    if function_name == 'criar_pedido_e_retornar_resumo':
                        function_response = fuction_to_call(
                            nome_cliente = function_args.get("nome_cliente"),
                            endereco_cliente = function_args.get("endereco_cliente"),
                            itens_pedido = function_args.get("itens_pedido"),
                            valor_total = function_args.get("valor_total"),
                            metodo_de_pagamento = function_args.get("metodo_de_pagamento"),
                            user = user, 
                            conversation = conversation,
                        )
                    context.append({
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    })

                    completions_after_function_response = openai.ChatCompletion.create(
                        model=model_name,
                        temperature=0,
                        messages=context
                    )

                    awnser = completions_after_function_response['choices'][0]['message']['content']
                    context.append({"role": "assistant", "content": awnser})
                    tokens_used = completions.usage['total_tokens'] + completions_after_function_response.usage['total_tokens']
                    
                else:
                    awnser = completions['choices'][0]['message']['content']
                    context.append({"role": "assistant", "content": awnser})
                    tokens_used = completions.usage['total_tokens']

            
            except Exception as e:
                awnser = CHAT_API_GENERAL_ERROR_MESSAGE
                tokens_used = 0

    return awnser, context, tokens_used

""" substituida por chamada de funcão
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
"""
