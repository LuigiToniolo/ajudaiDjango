from ..ContentExtractor import ContentExtractor

extractor = ContentExtractor()

def ai_gpt_extrair_resposta_de_FAQ(pergunta_do_cliente, faq):
    instructions = f"Você é um assistente especializado em assimilar a pergunta do cliente com o conteúdo do FAQ: {faq}. Responda sempre de forma curta e objetiva, se restringindo sempre às infomações contidas no FAQ."
    instructions = instructions + f"Ao receber a pergunta, informe, caso encontre a pergunta no FAQ, responda: '[resposta]' " 
    instructions = instructions + f"Caso não localizar uma resposta para a pergunta do cliente dentro do faq, responda: 'infelizmente não consigo te ajudar nesse caso, fale com um atendente' "

    user_message = f"Pergunta do cliente: {pergunta_do_cliente}"
    
    return extractor.extract(instructions=instructions, user_message=user_message)