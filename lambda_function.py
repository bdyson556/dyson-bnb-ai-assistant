import json
import os
import logging

from openai_service import generate_response
# from api_utils import register_webhook, verify_request_signature
from whatsapp_utils import is_valid_whatsapp_message, process_text_for_whatsapp, verify_request_signature, \
    register_webhook, send_whatsapp_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

APP_SECRET = os.environ["APP_SECRET"]  # Ensure you've set APP_SECRET in your Lambda environment variables


def lambda_handler(event, context):

    # Verify event signature  (docs: https://developers.facebook.com/docs/messenger-platform/webhooks/#validate-payloads )
    try:
        if verify_request_signature(event, APP_SECRET):
            logger.info("Signature verified.")
            # Process the request here
        else:
            logger.error("Signature verification failed.")
            # Handle unverified request here
    except ValueError as e:
        print(str(e))
        # Handle exception for failed verification

    # If new connection, register webhook
    if 'queryStringParameters' in event:
        return register_webhook(event)

    # Else, handle normal request
    else:
        logger.info("Not a service connection request.")
        logger.info(f"Incoming event:\n\t{event}")

        body = json.loads(event['body'])
        # if body.get('object'):
        if is_valid_whatsapp_message(body):
            entry = body['entry'][0]
            changes = entry['changes'][0]
            message = changes['value']['messages'][0]

            # Parse message...
            phone_number_id = changes['value']['metadata']['phone_number_id']  # TODO:  This is the WhatsApp business number, NOT the guest's number.
            from_number = message['from']  # 'from' is a reserved keyword in Python, so we use 'from_number'
            wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
            name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
            message = body["entry"][0]["changes"][0]["value"]["messages"][0]
            message_body = message["text"]["body"]
            # consider modifying and using whatsapputils process msg

            # OpenAI Integration
            # TODO activate new gen_response func
            response = generate_response(message_body, wa_id, name)
            response = process_text_for_whatsapp(response)

            ## TODO
            data = json.dumps({  # How to send text messages (including msg formatting, etc.): https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages#text-messages
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": from_number,
                # "type": "template",
                # "template": {"name": "hello_world", "language": {"code": "en_US"}}
                "type": "text",  # NOTE! In order to send text messages, user MUST have sent the number a message within 24 hours.
                "text": {"preview_url": True, "body": "Hello from Brady's app!"}
                # "text": {"body": "Hello from Brady's app!"}
                # "text": {"body": "Hello from AWS Lambda!"}
            })

            logger.info(f"Response to be sent:\n\t{data}")

            send_whatsapp_response(data, phone_number_id)

            return {
                'statusCode': 200,
                'body': json.dumps('Request processed successfully.'),
            }
