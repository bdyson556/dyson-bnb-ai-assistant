import unittest

from lambda_function import lambda_handler


class TestLambdaFunction(unittest.TestCase):

    def test_lambda_function(self):
        event = {'version': '2.0', 'routeKey': '$default', 'rawPath': '/webhook', 'rawQueryString': '', 'headers': {
            'x-hub-signature-256': 'sha256=284a91e37e4c86d296109945f76fc60ae11eee8902884c829cdd9a1f222350a5',
            'content-length': '469', 'x-amzn-tls-version': 'TLSv1.3', 'x-forwarded-proto': 'https',
            'x-forwarded-port': '443', 'x-forwarded-for': '2a03:2880:10ff:15::face:b00c', 'accept': '*/*',
            'x-amzn-tls-cipher-suite': 'TLS_AES_128_GCM_SHA256',
            'x-amzn-trace-id': 'Root=1-65eb3b00-525202d913f7d8c74414ed44',
            'host': 'i4vrxlf5toaxqvtkz3zqczjmsm0vwukg.lambda-url.us-east-1.on.aws', 'content-type': 'application/json',
            'accept-encoding': 'deflate, gzip', 'user-agent': 'facebookexternalua',
            'x-hub-signature': 'sha1=b1f89d6e4c67ca1f9f8fb40d25d5b439a2ef0924'},
                 'requestContext': {'accountId': 'anonymous', 'apiId': 'i4vrxlf5toaxqvtkz3zqczjmsm0vwukg',
                                    'domainName': 'i4vrxlf5toaxqvtkz3zqczjmsm0vwukg.lambda-url.us-east-1.on.aws',
                                    'domainPrefix': 'i4vrxlf5toaxqvtkz3zqczjmsm0vwukg',
                                    'http': {'method': 'POST', 'path': '/webhook', 'protocol': 'HTTP/1.1',
                                             'sourceIp': '2a03:2880:10ff:15::face:b00c',
                                             'userAgent': 'facebookexternalua'},
                                    'requestId': 'cbd81a57-8964-4c92-b657-47a2fc112bba', 'routeKey': '$default',
                                    'stage': '$default', 'time': '08/Mar/2024:16:21:20 +0000',
                                    'timeEpoch': 1709914880544},
                 'body': '{"object":"whatsapp_business_account","entry":[{"id":"268325799688623","changes":[{"value":{"messaging_product":"whatsapp","metadata":{"display_phone_number":"15550195686","phone_number_id":"274515802405177"},"contacts":[{"profile":{"name":"Brady Dyson"},"wa_id":"16125187161"}],"messages":[{"from":"16125187161","id":"wamid.HBgLMTYxMjUxODcxNjEVAgASGBQzQTU0NEY4MjVFNUI3RUM1RUJCNgA=","timestamp":"1709914880","text":{"body":"Hi"},"type":"text"}]},"field":"messages"}]}]}',
                 'isBase64Encoded': False}

        lambda_handler(event, "")

if __name__ == "__main__":
    unittest.main()