import requests
import json

def send_response(page_id, auth_token, to_number, message_text):
    graph_api_version = 'v17.0'
    url = f"https://graph.facebook.com/{graph_api_version}/{page_id}/messages"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": str(to_number),
        "type": "text",
        "text": {
            'body': message_text
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    try:
        print(f'[WHATSAPP][HTTP] POST {url} to={to_number} status={response.status_code} body={response.text[:500]}')
    except Exception:
        pass

    return response