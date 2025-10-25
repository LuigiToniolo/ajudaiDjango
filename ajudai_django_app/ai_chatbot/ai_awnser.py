from .openai_client import get_openai_client
import json
from ajudai_django_app.ai_chatbot.ai_extration import ai_gpt_extrair_preco_do_cardapio
from ajudai_django_app.ai_chatbot.ai_tools import count_tokens, instruction_builder, messages_to_string
from ajudai_django_app.models import ChatBot, Pedido
from constants import AWNSER_WHEN_MESSAGE_IS_OVER_THE_LIMIT, CHAT_API_GENERAL_ERROR_MESSAGE, CHAT_API_MESSAGE_AND_AWNSER_OVERLIMT_EVEN_TRYING_TO_SHORT, FECHAR_PEDIDO_ERROR_MESSAGE_FUNCTION_CALL, MIN_TOKEN_LIMIT_RATE_LEFT_TO_AWNSER, TOKEN_LIMIT_MARGIN

# AUTO AVALIAR
from ajudai_django_app.ai_chatbot.AutoAvaliar.ai_extraction import ai_gpt_extrair_resposta_de_FAQ
# NOTIFICACAO
from notifications.signals import notify
import sys

from get_secret_variables import get_secret_var
client = get_openai_client()

def obeter_precos_itens_cardapio(itens_do_cardapio, chatbot_id):
    try:
        chatbot = ChatBot.objects.get(
                    id=chatbot_id,
                    )
        cardapio = chatbot.cardapio
        return ai_gpt_extrair_preco_do_cardapio(itens_do_cardapio, cardapio)
    except:
        return 'Não foi possível extrair informações do cardápio'

def criar_pedido_e_retornar_resumo(
        nome_cliente,
        cpf_cliente,
        data_agendamento,
        email_cliente,
        endereco_cliente,
        itens_pedido,
        taxa_de_entrega,
        valor_total,
        metodo_de_pagamento,
        user,
        conversation
    ):
    print('Objetos pegos da função criar_pedido_e_retornar_resumo:')
    print(nome_cliente)
    print(cpf_cliente)
    print(data_agendamento)
    print(email_cliente)
    print(endereco_cliente)
    print(itens_pedido)
    print(taxa_de_entrega)
    
    resumo_do_pedido = f"Seu pedido foi confirmado! \nResumo do Pedido:\n - Nome do Cliente: {nome_cliente} \n - CPF do cliente: {cpf_cliente} \n - Data de agendamento: {data_agendamento} \n - E-mail cliente: {email_cliente} \n - Itens do pedido: {itens_pedido} \n - Total do pedido: {valor_total} \n - Método de Pagamento: {metodo_de_pagamento} \n - Endereço: {endereco_cliente}"
    Pedido.criar_novo_pedido_ja_com_parametros(nome_cliente, cpf_cliente, data_agendamento, email_cliente, endereco_cliente, itens_pedido, taxa_de_entrega, valor_total, metodo_de_pagamento, resumo_do_pedido, user, conversation)
    return 'Pedido feito com sucesso'


### AUTO AVALIAR
def obter_resposta_faq(mensagem_usuario, chatbot_id):
    try:
        chatbot = ChatBot.objects.get(
                    id=chatbot_id,
                    )
        faq = chatbot.cardapio
        return ai_gpt_extrair_resposta_de_FAQ(mensagem_usuario, faq)
    except:
        return 'Não foi possível extrair informações do FAQ'


### NOTIFICAÇÃO
def notificar_admin_problema(mensagem, chatbot_id, user, conversation):
    try:
        chatbot = ChatBot.objects.get(
                    id=chatbot_id,
                    )
        notify.send(chatbot, recipient=user, verb=mensagem, target=conversation, description=f'O cliente de numero {conversation.company_client_number} está precisando de atendimento humano.')
        return 'Um administrador recebeu uma notificação, aguarde uns instantes'
    except Exception as e:
        print(f"Erro ao notificar admin {e}", file=sys.stderr)
        return 'Não foi possivel notificar um administrador'

def generate_gpt_response(prompt, context, role, aditional_instructions, model_name, model_token_limit, chatbot_id, user, conversation):
    instructions = instruction_builder(aditional_instructions, role)
    token_limit = model_token_limit
    chatbot = ChatBot.objects.get(id=chatbot_id)
    functions = []
    if chatbot.chatbot_has_products_catalog == False:
        functions = [
            {
                "name": "obeter_precos_itens_cardapio",
                "description": chatbot.descricao_funcao_cardapio,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "itens_do_cardapio": {
                            "type": "string",
                            "description": 'Itens do cardápio solictados/pedidos pelo cliente (Exemplo: Um X-Burger e uma Coca-Cola em lata)',
                        },
                    },
                    "required": ["itens_do_cardapio"],
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
                        "cpf_cliente": {
                            "type": "string",
                            "description": 'CPF do cliente',
                        },
                        "data_agendamento": {
                            "type": "string",
                            "description": 'Data de agendamento da faxina',
                        },
                        "email_cliente": {
                            "type": "string",
                            "description": 'E-mail do cliente',
                        },
                        "endereco_cliente": {
                            "type": "string",
                            "description": 'Caso a opção seja por entrega, fornecer o Endereço do cliente completo, inclusive com o CEP. Caso a opção seja por retirada no balção, fornecer o endereço do Estbelecimento',
                        },
                        "itens_pedido": {
                            "type": "string",
                            "description": 'Itens do pedido do cliente, cada qual o respectivo preço. Inserir a taxa de entrega como um item caso a opção seja de entrega (e não retirada no balcão) (exemplo: Pizza de Mussarela Grande - R$ 45,00; Cola Cola lata - R$ 5,00; Taxa de Entrega R$ 5,00;)',
                        },
                        "taxa_de_entrega": {
                            "type": "string",
                            "description": 'Taxa de Entrega. Caso o cliente tenha optado por retirar no balcão, o valor é R$0,00 (retirar no balcão)',
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
                    "required": ["nome_cliente", "cpf_cliente", "email_cliente", "data_agendamento", "endereco_cliente", "itens_pedido"],
                },
            },
        ]
    else:
        #TODO AVALAR AQUI COMO VAI SER A CRIAÇÃO DO RESUMO DO PEDIDO CASO HAJA O CATÁLOGO, principalmente em relação aos itens do pedido
        functions = [
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
                        "cpf_cliente": {
                            "type": "string",
                            "description": 'CPF do cliente',
                        },
                        "data_agendamento": {
                            "type": "string",
                            "description": 'Data de agendamento da faxina',
                        },
                        "email_cliente": {
                            "type": "string",
                            "description": 'E-mail do cliente',
                        },
                        "endereco_cliente": {
                            "type": "string",
                            "description": 'Caso a opção seja por entrega, fornecer o Endereço do cliente completo, inclusive com o CEP. Caso a opção seja por retirada no balção, fornecer o endereço do Estbelecimento',
                        },
                        "itens_pedido": {
                            "type": "string",
                            "description": 'Itens do pedido do cliente, cada qual o respectivo preço. Inserir a taxa de entrega como um item caso a opção seja de entrega (e não retirada no balcão) (exemplo: Pizza de Mussarela Grande - R$ 45,00; Cola Cola lata - R$ 5,00; Taxa de Entrega R$ 5,00;)',
                        },
                        "taxa_de_entrega": {
                            "type": "string",
                            "description": 'Taxa de Entrega. Caso o cliente tenha optado por retirar no balcão, o valor é R$0,00 (retirar no balcão)',
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
                    "required": ["nome_cliente", "cpf_cliente", "email_cliente","data_agendamento", "endereco_cliente", "itens_pedido"],
                },
            },
        ]

    # AUTO AVALIAR
    functions += [
        {
            "name": "obter_resposta_do_faq",
            "description": chatbot.descricao_funcao_cardapio,
            "parameters": {
                "type": "object",
                "properties": {
                    "resposta_faq": {
                        "type": "string",
                        "description": 'Resposta da pergunta frequente (FAQ) feita pelo cliente.',
                    },
                },
                "required": ["resposta_faq"],
            },
        },
    ]
    
    
    # NOTIFICACAO
    functions += [
        {
            "name": "notificar_admin",
            "description": 'Notifica o administrador do chatbot sobre que um cliente teve um problema',
            "parameters": {
                "type": "object",
                "properties": {
                    "mensagem": {
                        "type": "string",
                        "description": 'Notificar um administrador de que um cliente precisa de algo.',
                    },
                },
                "required": ["mensagem"],
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
                completions = client.chat.completions.create(
                    model=model_name,
                    temperature=0,
                    messages=context,
                    functions=functions,
                    function_call="auto",
                )
                tokens_used = completions.usage.total_tokens

                response_message = completions.choices[0].message
                if response_message.get("function_call"):
                    available_functions = {
                        "criar_pedido_e_retornar_resumo": criar_pedido_e_retornar_resumo,
                        "obter_resposta_do_faq": obter_resposta_faq,
                        "notificar_admin": notificar_admin_problema,
                    }
                    if chatbot.chatbot_has_products_catalog == False:
                        available_functions["obeter_precos_itens_cardapio"] =  obeter_precos_itens_cardapio
                        
                    function_name = response_message["function_call"]["name"]
                    fuction_to_call = available_functions[function_name]
                    function_args = json.loads(response_message["function_call"]["arguments"])
                    if function_name == 'obeter_precos_itens_cardapio' and chatbot.chatbot_has_products_catalog == False:
                        function_response = fuction_to_call(
                            itens_do_cardapio=str(function_args.get("itens_do_cardapio")),
                            chatbot_id=chatbot_id,
                        )
                        #AQUI, CASO NECESSÁRIO, PODE SER NECESSÁRIO PADRONIZAR UM FUCNTION RESPONSSE PARA CASO NÃO ACHE NO CARDÁPIO E FAZER UMA RESPOSTA TRAVADA, SEM CHAMAR O COMPLETION
                        context.append({
                            "role": "function",
                            "name": function_name,
                            "content": function_response,
                        })

                        completions_after_function_response = client.chat.completions.create(
                            model=model_name,
                            temperature=0,
                            messages=context
                        )
                        awnser = completions_after_function_response.choices[0].message.content
                        context.append({"role": "assistant", "content": awnser})
                        tokens_used = tokens_used + completions_after_function_response.usage.total_tokens

                    if function_name == 'criar_pedido_e_retornar_resumo':
                        try:
                            function_response = fuction_to_call(
                                nome_cliente = str(function_args.get("nome_cliente")),
                                cpf_cliente = str(function_args.get("cpf_cliente")),
                                data_agendamento = str(function_args.get("data_agendamento")),
                                email_cliente = str(function_args.get("email_cliente")),
                                endereco_cliente = str(function_args.get("endereco_cliente")),
                                itens_pedido = str(function_args.get("itens_pedido")),
                                taxa_de_entrega = str(function_args.get("taxa_de_entrega")),
                                valor_total = str(function_args.get("valor_total")),
                                metodo_de_pagamento = str(function_args.get("metodo_de_pagamento")),
                                user = user,
                                conversation = conversation,
                            )
                            context.append({
                                "role": "function",
                                "name": function_name,
                                "content": function_response,
                            })

                            awnser =  'Seu pedido foi registrado com sucesso! Te informaremos por aqui de qualquer atualização. Muito obrigado!'
                            context.append({"role": "assistant", "content": awnser})

                        except Exception as e:
                            
                            print(f'Erro ao chamar a função de fechamento de pedido: {e}')

                            awnser = FECHAR_PEDIDO_ERROR_MESSAGE_FUNCTION_CALL
                            function_response = 'Não foi possível realizar o fechamento do pedido. Tente novamente ou aguarde até que um atendente humano assuma a conversa'
                            
                            context.append({
                                "role": "function",
                                "name": function_name,
                                "content": function_response,
                            })

                            context.append({"role": "assistant", "content": awnser})
                    
                    # AUTO AVALIAR    
                    if function_name == 'obter_resposta_do_faq':
                        function_response = fuction_to_call(
                            mensagem_usuario=str(function_args.get("resposta_faq")),
                            chatbot_id=chatbot_id,
                        )
                        context.append({
                            "role": "function",
                            "name": function_name,
                            "content": function_response,
                        })

                        completions_after_function_response = client.chat.completions.create(
                            model=model_name,
                            temperature=0,
                            messages=context
                        )
                        awnser = completions_after_function_response.choices[0].message.content
                        context.append({"role": "assistant", "content": awnser})
                        tokens_used = tokens_used + completions_after_function_response.usage.total_tokens

                    # NOTIFICACAO  
                    if function_name == 'notificar_admin':
                        function_response = fuction_to_call(
                            mensagem=str(function_args.get("mensagem")),
                            chatbot_id=chatbot_id,
                            user=user,
                            conversation=conversation,
                        )
                        
                        
                        # context.append({
                        #     "role": "function",
                        #     "name": function_name,
                        #     "content": function_response,
                        # })

                        # completions_after_function_response = openai.ChatCompletion.create(
                        #     model=model_name,
                        #     temperature=0,
                        #     messages=context
                        # )

                        awnser = "Iremos notificar um administrador, aguarde uns instantes!"
                        context.append({"role": "assistant", "content": awnser})
                        # tokens_used = tokens_used + completions_after_function_response.usage['total_tokens']

                else:
                    awnser = completions.choices[0].message.content
                    context.append({"role": "assistant", "content": awnser})


            except Exception as e:
                print(e, file=sys.stderr)
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