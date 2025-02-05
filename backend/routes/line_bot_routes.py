from flask import Blueprint, request, abort, jsonify, session, redirect
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction,
    URIAction
)
from backend.config.line_bot_config import LINE_CONFIG
from backend.config.database import get_db_connection
import json
from urllib.parse import quote
import requests
from flask_cors import CORS

line_bot_bp = Blueprint('line_bot', __name__)
CORS(line_bot_bp)

# 请替换为你的 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = 'hlgPhkQlTYeyDRVPqUsHXuUgPfQ7qFmvr02nksJWZzbSdi1OY0H0O8Z4wyTYyx91jRQoNR3esLEahiXJx9D/t0PNJNvJ4j70SOtqP2f4h6mPgDWzWv8eqVW2jfavfdwA6g3wsNietJRSmsYs1LMazwdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'b589c6bf4730e82dcfba0550a300111d'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@line_bot_bp.route("/generate-bind-url", methods=['POST'])
def generate_bind_url():
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        
        if not customer_id:
            return jsonify({
                "status": "error",
                "message": "缺少客戶ID"
            }), 400
            
        # 使用 LIFF URL，确保 customer_id 正确传递
        line_login_url = (
            f"https://liff.line.me/{LINE_CONFIG['LIFF_ID']}"
            f"?customer_id={customer_id}"
        )
        print(f"Generated LIFF URL: {line_login_url}")  # 添加调试日志
        
        return jsonify({
            "status": "success",
            "data": {
                "url": line_login_url
            }
        })
        
    except Exception as e:
        print(f"Error generating bind URL: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

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

@line_bot_bp.route("/line-binding", methods=['GET'])
def line_login_callback():
    try:
        # 获取授权码和状态
        code = request.args.get('code')
        state = request.args.get('state')  # state 中包含了 customer_id
        error = request.args.get('error')
        error_description = request.args.get('error_description')

        if error:
            return jsonify({
                "status": "error",
                "message": error_description or "授權失敗"
            }), 400

        if not code or not state:
            return jsonify({
                "status": "error",
                "message": "缺少必要參數"
            }), 400

        # 使用授权码获取访问令牌
        token_url = "https://api.line.me/oauth2/v2.1/token"
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": LINE_CONFIG['LIFF_ENDPOINT'],
            "client_id": LINE_CONFIG['CHANNEL_ID'],
            "client_secret": LINE_CONFIG['CHANNEL_SECRET']
        }
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if 'error' in token_json:
            raise Exception(f"獲取訪問令牌失敗: {token_json.get('error_description')}")

        # 使用访问令牌获取用户信息
        profile_url = "https://api.line.me/v2/profile"
        headers = {
            "Authorization": f"Bearer {token_json['access_token']}"
        }
        profile_response = requests.get(profile_url, headers=headers)
        profile_json = profile_response.json()

        if 'error' in profile_json:
            raise Exception(f"獲取用戶信息失敗: {profile_json.get('error_description')}")

        # 绑定 LINE 账号
        bind_response = bind_line_account(state, profile_json['userId'])
        
        if bind_response.status_code != 200:
            raise Exception(f"綁定失敗: {bind_response.json().get('message')}")

        # 重定向到前端绑定成功页面
        return redirect(f"{LINE_CONFIG['FRONTEND_URL']}/account-settings")

    except Exception as e:
        print(f"Error in LINE login callback: {str(e)}")
        error_message = str(e)
        return redirect(f"{LINE_CONFIG['FRONTEND_URL']}/account-settings?error={quote(error_message)}")

@line_bot_bp.route("/bind", methods=['POST', 'OPTIONS'])
def bind():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        line_user_id = data.get('line_user_id')
        
        if not customer_id or not line_user_id:
            return jsonify({
                "status": "error",
                "message": "缺少必要參數"
            }), 400
            
        return bind_line_account(customer_id, line_user_id)
        
    except Exception as e:
        print(f"Error in bind: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def bind_line_account(customer_id, line_user_id):
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed")
            
        cursor = conn.cursor()
        
        # 檢查是否已經綁定
        cursor.execute("""
            SELECT id FROM customers 
            WHERE line_account = %s AND id != %s
        """, (line_user_id, customer_id))
        
        if cursor.fetchone():
            raise Exception("此LINE帳號已被其他客戶綁定")
        
        # 更新客戶的LINE帳號
        cursor.execute("""
            UPDATE customers 
            SET line_account = %s,
                updated_at = NOW()
            WHERE id = %s AND status = 'active'
            RETURNING id, company_name
        """, (line_user_id, customer_id))
        
        result = cursor.fetchone()
        if not result:
            raise Exception("找不到客戶資料或客戶狀態不正確")
            
        conn.commit()
        
        # 發送歡迎訊息和好友邀請
        try:
            # 創建歡迎訊息模板
            welcome_message = TemplateSendMessage(
                alt_text='歡迎使用我們的服務',
                template=ButtonsTemplate(
                    title='帳號綁定成功！',
                    text=f'歡迎使用我們的服務\n請點擊下方按鈕加入好友以開始使用',
                    actions=[
                        URIAction(
                            label='加入好友',
                            uri=f'https://line.me/R/ti/p/@{LINE_CONFIG["BOT_BASIC_ID"]}'
                        )
                    ]
                )
            )
            
            # 發送訊息
            line_bot_api.push_message(
                line_user_id,
                welcome_message
            )
        except Exception as e:
            print(f"Error sending welcome message: {str(e)}")
        
        return jsonify({
            "status": "success",
            "message": "LINE帳號綁定成功"
        })
        
    except Exception as e:
        raise Exception(f"綁定失敗: {str(e)}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 檢查用戶是否已綁定
        cursor.execute("""
            SELECT id, company_name FROM customers 
            WHERE line_account = %s AND status = 'active'
        """, (user_id,))
        
        customer = cursor.fetchone()
        
        if customer:
            if user_message == '查看訂單':
                # 這裡可以加入查看訂單的邏輯
                reply_text = f"您好 {customer[1]}，您可以透過以下連結查看訂單狀態..."
            else:
                reply_text = f"您好 {customer[1]}，很高興為您服務！\n請問需要什麼協助？"
        else:
            reply_text = "您尚未綁定帳號，請先完成帳號綁定。"
            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        
    except Exception as e:
        print(f"Error handling message: {str(e)}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="抱歉，系統發生錯誤，請稍後再試。")
        )
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close() 