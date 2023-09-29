import requests
import json

def send_products_catalog(page_id, auth_token, to_number, title_text, body_text, footer_text, catalog_id, sections_and_products_list):
    graph_api_version = 'v17.0'
    url = f"https://graph.facebook.com/{graph_api_version}/{page_id}/messages"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "recipient_type": "individual",
        "to" : str(to_number),
        "type": "interactive" ,
        "interactive":{
            "type": "product_list",
            "header": {
                "type": "text",
                "text": title_text
            },
            "body": {
                "text": body_text,
            },
            "footer": {
                "text": footer_text
            },
            "action": {
                "catalog_id" : catalog_id,
                "sections" : sections_and_products_list,
            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    return response