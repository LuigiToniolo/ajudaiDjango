import openai
from constants import GPT3_MODEL_NAME
from get_secret_variables import get_secret_var

openai.api_key = get_secret_var("OPENAI_API_KEY")

def ai_gpt_extrair_dado_do_resumo(dado_a_extrair, resumo_do_pedido):
    intructions = 'Você é um assistente prestativo que responde de forma objetiva e apenas o que te foi solicitado'
    completions = openai.ChatCompletion.create(
                    model=GPT3_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": intructions},
                        {
                            "role": "user", 
                            "content": f'Do seguinte texto: {resumo_do_pedido}, extraia o seguinte dado: {dado_a_extrair}. A sua resposta deve conter apenas o(a) {dado_a_extrair}, e nada mais. Caso não encontre esse dado, retorne o seguinte texto texto como resposta: "Não foi possível extrair o dado da conversa'
                        },
                    ]
                )

    return completions['choices'][0]['message']['content']

def ai_gpt_extrair_informacao_do_cardapio(dado_a_extrair, cardapio):
    intructions = 'Você é um assistente prestativo que responde de forma objetiva e apenas o que te foi solicitado'
    completions = openai.ChatCompletion.create(
                    model=GPT3_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": intructions},
                        {
                            "role": "user", 
                            "content": f'Do seguinte cardápio: {cardapio}, extraia o seguinte dado: {dado_a_extrair}. Caso não encontre esse dado, retorne o seguinte texto texto como resposta: "Não foi possível encontrar a informação que você busca no cardápio. Por favor, consulte o link com o cardápio na íntegra (se ainda nao te passei o link, peca novamente que eu pe forneço)'
                        },
                    ]
                )

    return completions['choices'][0]['message']['content']
