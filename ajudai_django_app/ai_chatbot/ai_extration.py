from constants import GPT3_MODEL_NAME
from .openai_client import get_openai_client

def ai_gpt_extrair_dado_do_resumo(dado_a_extrair, resumo_do_pedido):
    intructions = 'Você é um assistente prestativo que responde de forma objetiva e apenas o que te foi solicitado'
    client = get_openai_client()
    completions = client.chat.completions.create(
                    model=GPT3_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": intructions},
                        {
                            "role": "user", 
                            "content": f'Do seguinte texto: {resumo_do_pedido}, extraia o seguinte dado: {dado_a_extrair}. A sua resposta deve conter apenas o(a) {dado_a_extrair}, e nada mais. Caso não encontre esse dado, retorne o seguinte texto texto como resposta: "Não foi possível extrair o dado da conversa'
                        },
                    ]
                )
    return completions.choices[0].message.content

def ai_gpt_extrair_endereco_do_resumo(resumo_do_pedido):
    intructions = 'Você é um assistente prestativo que responde de forma objetiva e apenas o que te foi solicitado'
    client = get_openai_client()
    completions = client.chat.completions.create(
                    model=GPT3_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": intructions},
                        {
                            "role": "user", 
                            "content": f'Do seguinte texto: {resumo_do_pedido}, caso haja a menção de retirada no balcão, retorne a resposta "retirada no balcão". Caso contrário, extraia o endereço de entrega e responda apenas com endereço de entrega, e nada mais.'
                        },
                    ]
                )
    return completions.choices[0].message.content

def ai_gpt_extrair_preco_do_cardapio(itens_do_cardapio, cardapio):
    instructions = f'Você é um assistente especializado em obter os preços dos itens contidos no seguinte cardápio {cardapio}. Responda sempre de forma curta e objectiva, se restringindo sempre às infomações obtidas no cardápio.'
    instructions = instructions + 'Ao receber os itens solictados, informe, para cada item localizado no cardápio: "o preço do item [item solictado] é [preço emcontrado]"'
    instructions = instructions +  'Para cada item em que você não localizar o preço no cardápio, responda: "o item [item solicitado] não está no cardápio. Peço para o cliente informar o nome do item exatamente como está no cardápio]"'
    client = get_openai_client()
    completions = client.chat.completions.create(
                    model=GPT3_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": instructions},
                        {
                            "role": "user", 
                            "content": f'Itens solicitados: {itens_do_cardapio}'
                        },
                    ]
                )
    return completions.choices[0].message.content
