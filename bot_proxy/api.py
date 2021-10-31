import os

if os.getenv('DEVELOPMENT') is not None:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path='../.env')

import sys
import requests
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage)
from prometheus_client.parser import text_string_to_metric_families

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET') or 'YOUR_SECRET'
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN') or 'YOUR_ACCESS_TOKEN'
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    message = event.message.text
    if message == 'a':
        prom_data = requests.get('http://api-deployment:31110/metrics')
        request_time = ['API time spent: \n']
        for family in text_string_to_metric_families(prom_data.content.decode('UTF-8')):
            for sample in family.samples:
                if sample[0] == 'process_cpu_seconds_total':
                    request_time.append(f'CPU time: {str(sample[2])}s\n')
                if sample[0] == 'server_requests_total':
                    request_time.append(f'API cost time: {str(sample[2])}s\n')
                    break
                # print("Name: {0} Labels: {1} Value: {2}".format(*sample))
        output = TextSendMessage(text=''.join(request_time))
    elif message == 'flex':
        # https://github.com/line/line-bot-sdk-python#flexsendmessage
        output = FlexSendMessage(
            alt_text='hello',
            contents={
                'type': 'bubble',
                'direction': 'ltr',
                'hero': {
                    'type': 'image',
                    'url': 'https://engineering.linecorp.com/wp-content/uploads/2021/04/%E6%88%AA%E5%9C%96-2021-04-23-%E4%B8%8B%E5%8D%883.00.15.png',
                    'size': 'full',
                    'aspectRatio': '100:100',
                    'aspectMode': 'cover',
                    'action': {'type': 'uri', 'uri': 'http://example.com', 'label': 'label'}
                }
            }
        )
    else:
        output = TextSendMessage(text="Just echo echo~~~")
    line_bot_api.reply_message(
        event.reply_token,
        output
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=31112, debug=True)

