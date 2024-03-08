import hashlib
import hmac
import logging
import http
import json
import os
import re
import shelve

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def register_webhook(event):
    # Register the webhook
    queryParams = event['queryStringParameters']
    verify_token = os.environ['VERIFY_TOKEN']

    mode = queryParams.get("hub.mode")
    token = queryParams.get("hub.verify_token")
    challenge = queryParams.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == verify_token:
            logger.info("WEBHOOK_VERIFIED")
            return {
                'statusCode': 200,
                'body': challenge
            }
        else:
            return {'statusCode': 403}


def verify_request_signature(event, app_secret):
    # Assuming the incoming event is the raw body from the Lambda function's event parameter
    signature = event['headers'].get("x-hub-signature-256", None)

    if not signature:
        print("Couldn't find 'x-hub-signature-256' in headers.")
        return False
    else:
        elements = signature.split("=")
        signature_hash = elements[1]
        expected_hash = hmac.new(
            bytes(app_secret, 'utf-8'),
            msg=event['body'].encode('utf-8'),  # Assuming 'event['body']' is the raw body as a string
            digestmod=hashlib.sha256
        ).hexdigest()

        if signature_hash != expected_hash:
            raise ValueError("Couldn't validate the request signature.")
        return True


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )


# TODO: replace http with requests
def send_whatsapp_response(data, phone_number_id):
    conn = http.client.HTTPSConnection('graph.facebook.com')
    headers = {'Content-Type': 'application/json'}
    path = f'/v12.0/{phone_number_id}/messages?access_token={os.environ["WHATSAPP_TOKEN"]}'
    conn.request("POST", path, body=data, headers=headers)
    response = conn.getresponse()
    res_body = response.read()
    logger.info(f"statusCode: {response.status}")
    logger.info(f"Response from WhatsApp API: {res_body}")

# TODO: review below to see if above can be enhanced.
# def send_message(data):
#     headers = {
#         "Content-type": "application/json",
#         "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
#     }
#
#     url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"
#
#     try:
#         response = requests.post(
#             url, data=data, headers=headers, timeout=10
#         )  # 10 seconds timeout as an example
#         response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
#     except requests.Timeout:
#         logging.error("Timeout occurred while sending message")
#         return jsonify({"status": "error", "message": "Request timed out"}), 408
#     except (
#         requests.RequestException
#     ) as e:  # This will catch any general request exception
#         logging.error(f"Request failed due to: {e}")
#         return jsonify({"status": "error", "message": "Failed to send message"}), 500
#     else:
#         # Process the response as normal
#         log_http_response(response)
#         return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


# Use context manager to ensure the shelf file is closed properly
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


# def process_whatsapp_message(body):
#     wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
#     name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
#
#     message = body["entry"][0]["changes"][0]["value"]["messages"][0]
#     message_body = message["text"]["body"]
#
#     # response = generate_response(message_body)
#
#     # OpenAI Integration
#     response = generate_response(message_body, wa_id, name)
#     response = process_text_for_whatsapp(response)
#
#     data = get_text_message_input(current_app.config["RECIPIENT_WA_ID"], response)
#     send_message(data)




# Check if it's a WhatsApp status update
#     if (
#         body.get("entry", [{}])[0]
#         .get("changes", [{}])[0]
#         .get("value", {})
#         .get("statuses")
#     ):
#         logging.info("Received a WhatsApp status update.")
#         return jsonify({"status": "ok"}), 200