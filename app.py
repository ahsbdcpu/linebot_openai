from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

openai_message_count = 0

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text1 = event.message.text
    
    # 定義 ChatGPT 的個性
    personality = {
        "role": "doctor", 
        "specialty": "pediatrician", 
        "ability": "provide medical advice and answer health-related questions",  
        "tone": "friendly and professional"  
    }
    
    # 使用 ChatGPT 生成回覆
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "user", "content": text1}
        ],
        model="gpt-3.5-turbo-0125",
        temperature=0.5,
        personality=personality  # 將定義的個性傳遞給模型
    )
    try:
        ret = response['choices'][0]['message']['content'].strip()
    except:
        ret = '發生錯誤！'
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()
