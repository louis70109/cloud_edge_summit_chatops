import os

if os.getenv('DEVELOPMENT') is not None:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path='../.env')
import json
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


@app.route("/", methods=['GET'])
def healthz():
    return 'OK'


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
    if message == '/status':
        prom_data = requests.get('http://localhost:31110/metrics')
        request_time = []
        for family in text_string_to_metric_families(prom_data.content.decode('UTF-8')):
            for sample in family.samples:
                if sample[0] == 'process_cpu_seconds_total':
                    request_time.append(f'CPU 花費時間: {str(sample[2])}秒')
                if sample[0] == 'my_requests_total':
                    sample_json = json.loads(json.dumps(sample[1]))
                    sample_str = f'路由：{sample_json["endpoint"]}'
                    request_time.append(sample_str)
                    sample_str = f'方法：{sample_json["method"]}'
                    request_time.append(sample_str)
                    request_time.append(f'失敗呼叫次數: {str(sample[2])}')
                if sample[0] == 'server_requests_total':
                    request_time.append(f'API 總呼叫時間: {str(sample[2])}秒')
                if sample[0] == 'python_info':
                    sample_json = json.loads(json.dumps(sample[1]))
                    request_time.append(f'Python 版本: {sample_json["version"]}')
                # More prometheus metrics input here :)

        # Flex Message building
        contents = []
        for idx in range(len(request_time)):
            if idx == 0:
                contents.append({
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "filler"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [],
                                    "cornerRadius": "30px",
                                    "height": "12px",
                                    "width": "12px",
                                    "borderColor": "#EF454D",
                                    "borderWidth": "2px"
                                },
                                {
                                    "type": "filler"
                                }
                            ],
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": request_time[idx],
                            "gravity": "center",
                            "flex": 4,
                            "size": "sm"
                        }
                    ],
                    "spacing": "lg",
                    "cornerRadius": "30px",
                    "margin": "xl"
                })
            else:
                contents.append({
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "filler"
                                        },
                                        {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [],
                                            "width": "2px",
                                            "backgroundColor": "#B7B7B7"
                                        },
                                        {
                                            "type": "filler"
                                        }
                                    ],
                                    "flex": 1
                                }
                            ],
                            "width": "12px"
                        },
                        {
                            "type": "text",
                            "text": " ",
                            "gravity": "center",
                            "flex": 4,
                            "size": "xs",
                            "color": "#8c8c8c"
                        }
                    ],
                    "spacing": "lg",
                    "height": "64px"
                })
                contents.append({
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "filler"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [],
                                    "cornerRadius": "30px",
                                    "width": "12px",
                                    "height": "12px",
                                    "borderWidth": "2px",
                                    "borderColor": "#6486E3"
                                },
                                {
                                    "type": "filler"
                                }
                            ],
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": request_time[idx],
                            "gravity": "center",
                            "flex": 4,
                            "size": "sm"
                        }
                    ],
                    "spacing": "lg",
                    "cornerRadius": "30px"
                })

        output = FlexSendMessage(
            alt_text='Item API 目前狀態',
            contents={
                "type": "bubble",
                "size": "mega",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "K3d",
                                    "color": "#ffffff66",
                                    "size": "sm"
                                },
                                {
                                    "type": "text",
                                    "text": "Item API 狀態",
                                    "color": "#ffffff",
                                    "size": "xl",
                                    "flex": 4,
                                    "weight": "bold"
                                }
                            ]
                        }
                    ],
                    "paddingAll": "20px",
                    "backgroundColor": "#0367D3",
                    "spacing": "md",
                    "height": "100px",
                    "paddingTop": "22px"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": contents
                }
            })
    else:
        output = TextSendMessage(text="Just echo echo~~~")
    line_bot_api.reply_message(
        event.reply_token,
        output
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
