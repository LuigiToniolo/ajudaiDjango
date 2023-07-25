import openai
from constants import GPT3_MODEL_NAME
from get_secret_variables import get_secret_var

openai.api_key = get_secret_var("OPENAI_API_KEY")

def ai_completion_gpt(solicitacao):
    intructions = 'Você é um assistente prestativo que responde de forma objetiva,apenas o que te foi solicitado'
    completions = openai.ChatCompletion.create(
                    model=GPT3_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": intructions},
                        {"role": "user", "content": solicitacao},
                    ]
                )

    return completions['choices'][0]['message']['content']

def extrair_nome_cliente_com_gpt(resumo_do_pedido):
    solicitacao = f'Baseando-se no seguinte texto: {resumo_do_pedido}, responda qual o nome do cliente. A sua resposta deve conter apenas o nome do cliente, e nada mais. Caso não encontre essa informação, retorne o seguinte texto texto como resposta: "Não foi possível extrair o nome do cliente da conversa"'
    return ai_completion_gpt(solicitacao)