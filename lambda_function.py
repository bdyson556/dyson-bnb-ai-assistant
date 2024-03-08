import json
import os
import logging

from openai_service import generate_response
# from api_utils import register_webhook, verify_request_signature
from whatsapp_utils import is_valid_whatsapp_message, process_text_for_whatsapp, verify_request_signature, \
    register_webhook, send_whatsapp_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    # Verify event signature  (docs: https://developers.facebook.com/docs/messenger-platform/webhooks/#validate-payloads )
    app_secret = os.environ.get("APP_SECRET")  # Ensure you've set APP_SECRET in your Lambda environment variables
    try:
        if verify_request_signature(event, app_secret):
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
            phone_number_id = changes['value']['metadata']['phone_number_id']
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

            data = json.dumps({
                "messaging_product": "whatsapp",
                "to": from_number,
                "text": {"body": "Hello from AWS Lambda!"}
            })

            logger.info(f"Response to be sent:\n\t{data}")

            send_whatsapp_response(data, phone_number_id)

            return {
                'statusCode': 200,
                'body': json.dumps('Request processed successfully.'),
            }

# Ensure you have VERIFY_TOKEN and WHATSAPP_TOKEN set in your Lambda function's environment variables
