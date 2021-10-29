import os

from linebot.models.events import VideoPlayCompleteEvent

if os.getenv('DEVELOPMENT') is not None:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path='../.env')

import sys

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, LocationSendMessage,
    VideoSendMessage, ImageSendMessage, StickerSendMessage,
)

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
    if message == 'emoji':
        emoji = [
            {
                "index": 0,
                "productId": "5ac1bfd5040ab15980c9b435",
                "emojiId": "001"
            },
            {
                "index": 13,
                "productId": "5ac1bfd5040ab15980c9b435",
                "emojiId": "002"
            }
        ]
        output = TextSendMessage(text='$ LINE emoji $', emojis=emoji)
    elif message == 'sticker':
        # https://github.com/line/line-bot-sdk-python#stickersendmessage
        output = StickerSendMessage(
            package_id='1',
            sticker_id='2'
        )
    elif message == 'image':
        # https://github.com/line/line-bot-sdk-python#imagesendmessage
        output = ImageSendMessage(
            original_content_url='https://engineering.linecorp.com/wp-content/uploads/2021/06/linebot001-1024x571.jpg',
            preview_image_url='https://engineering.linecorp.com/wp-content/uploads/2021/06/linebot001-1024x571.jpg'
        )

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
    app.run(host='0.0.0.0', port=5000, debug=True)

