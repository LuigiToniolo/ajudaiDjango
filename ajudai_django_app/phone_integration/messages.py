from get_secret_variables import get_secret_var
import requests


def send_response(page_id, auth_token, to_number, message_text):
    #TODO REVER ESSE CÓDIGO COM A DOCUMENTAÇÃO DO META WHATSAPP API
    graph_api_version = "v16.0"
    endpoint = f"https://graph.facebook.com/{graph_api_version}/{page_id}/messages"


    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}',
    }
    
    payload = {
        'to': to_number,
        'type': 'text',
        'text': {
            'body': message_text
        }
    }
    
    response = requests.post(endpoint, headers=headers, json=payload)
    return response.json()

