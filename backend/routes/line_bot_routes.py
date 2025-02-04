from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction
)

line_bot_bp = Blueprint('line_bot', __name__)

# 请替换为你的 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = 'hlgPhkQlTYeyDRVPqUsHXuUgPfQ7qFmvr02nksJWZzbSdi1OY0H0O8Z4wyTYyx91jRQoNR3esLEahiXJx9D/t0PNJNvJ4j70SOtqP2f4h6mPgDWzWv8eqVW2jfavfdwA6g3wsNietJRSmsYs1LMazwdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'b589c6bf4730e82dcfba0550a300111d'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@line_bot_bp.route("/callback", methods=['POST'])
def callback():
    # 获取 X-Line-Signature 头部值
    signature = request.headers['X-Line-Signature']

    # 获取请求体内容
    body = request.get_data(as_text=True)

    try:
        # 验证签名
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    
    if user_message == '查看產品':
        # 从数据库获取产品信息并回复
        reply_text = "以下是我們的產品列表：\n1. 產品A\n2. 產品B\n3. 產品C"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    
    elif user_message == '訂單查詢':
        # 创建按钮模板
        buttons_template = ButtonsTemplate(
            title='訂單查詢',
            text='請選擇要查詢的訂單類型',
            actions=[
                PostbackTemplateAction(
                    label='最近訂單',
                    data='action=recent_orders'
                ),
                PostbackTemplateAction(
                    label='待處理訂單',
                    data='action=pending_orders'
                )
            ]
        )
        template_message = TemplateSendMessage(
            alt_text='訂單查詢選單',
            template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    
    else:
        # 默认回复
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="您好！我是客服機器人，請問需要什麼幫助？\n- 輸入「查看產品」查看產品列表\n- 輸入「訂單查詢」查詢訂單狀態")
        ) 