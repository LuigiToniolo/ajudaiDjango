from datetime import datetime

def merge_context_and_display_time(conversas):
    conversas_com_tempo_das_mensagens = []
    for conversa in conversas:
        if len(conversa.context) == len(conversa.messages_display_time):
            merged_context = []
            for i in range(len(conversa.context)):
                # Merge dictionaries at the same index
                merged_item = {**conversa.context[i], **conversa.messages_display_time[i]}
                merged_context.append(merged_item)
            # Replace the original context with the merged context
            conversa.context = merged_context
            # Append the updated conversa object to the new list
            conversas_com_tempo_das_mensagens.append(conversa)
        else:
            # handle the case when the lengths don't match, e.g., log an error or raise an exception
            pass
    return conversas_com_tempo_das_mensagens

def group_and_sort_messages(conversas, sort_order='asc'):
    ''' 
        Essa função recebe as conversas com data e horário nas mensagens (context)
        e ordena tanto as conversas quanto as mensagens dentro do context
    '''
    
    # Group chats that have the same client number and chatbot
    chats_grouped_by_client_phone_number = []
    for conversa in conversas:
        already_inserted = False
        if(not conversa in chats_grouped_by_client_phone_number):
            for i in range(len(chats_grouped_by_client_phone_number)):
                grouped_chat = chats_grouped_by_client_phone_number[i]
                # If already exists a chat with the current chatbot and cellphone number, just append one context in another
                if(grouped_chat.chatbot == conversa.chatbot and grouped_chat.company_client_number == conversa.company_client_number):
                    grouped_chat.context.extend(entry for entry in conversa.context if entry['role'] in ('user', 'assistant'))
                    if(not conversa.last_message_shown):
                        grouped_chat.last_message_shown = conversa.last_message_shown
                        grouped_chat.id = conversa.id
                    already_inserted = True
                    continue
                
            if(not already_inserted):
                chats_grouped_by_client_phone_number.append(conversa)
                
    # Ordena mensagens em cada chat
    for chat in chats_grouped_by_client_phone_number:
        chat.context.sort(
            key=lambda m:
                datetime.combine(
                    datetime.strptime(m['date'], '%d/%m/%Y'),
                    datetime.time(
                        datetime.strptime(m['time'], '%H:%M')
                    )
                )
        )
    
    # Ordena chats pela ultima mensagem
    chats_grouped_by_client_phone_number.sort(
        key=lambda c: 
            datetime.combine(
                datetime.strptime(c.context[-1]['date'], '%d/%m/%Y'), 
                datetime.time(
                    datetime.strptime(c.context[-1]['time'], '%H:%M')
                )
            ), 
            reverse=sort_order == 'desc'
    )
    
    return chats_grouped_by_client_phone_number