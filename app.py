import re
from datetime import timedelta,datetime

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from linebot.exceptions import LineBotApiError

from dcard_tool import Dcardcrawler,weight_care_new_json
import time
import requests
import random
import json
import pandas as pd
import datetime
import emoji
# 
# import mongodb
# import scheduler


# init flask
app = Flask(__name__)
line_bot_api = LineBotApi('vFPL8j39qWb8HtHNOZKzlLV1hEVIjjEssSI0EJ61c+P2aGLVAbtEHGBbG6ld+4E5emRL+8u3MBZRSfKQVdi18QeOf/QXoiXhPWXYfTS05w0qKggHlCd2WgHHQovvbKQOZUZOkdo4nt0oeB2SZBT5twdB04t89/1O/w1cDnyilFU=
')
handler = WebhookHandler('1da69efc27acc97eadee26cf142d99b6')


# for alarm sys from fb app

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # print("body:",body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# welcome words
@handler.add(FollowEvent)
def handle_follow(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    nameid = profile.display_name
    uid = profile.user_id
    print(nameid)
    print(uid)
    # mongodb.save_userInfo(nameid, uid, message_text=None, reply_token=None, data_id = 'userinfo')
    
    buttons_template = TemplateSendMessage(
        alt_text='目錄',
        template=ButtonsTemplate(
            title='您好～ 台評會IR小幫手',
            text="提供您新聞學校每日新聞、台評會正負面口碑",
            thumbnail_image_url='https://i.imgur.com/jpnKztr.jpg',
            actions=[
                MessageTemplateAction(
                    label='點我進入',
                    text='點我進入'
                )
            ]
        )
    )
    
    
    

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
    text = event.message.text
    profile = line_bot_api.get_profile(event.source.user_id)
    nameid = profile.display_name
    uid = profile.user_id
    print('nameid:', nameid)
    print('uid:', uid)


    # get user data.
    # userinfo = mongodb.get_school_by_userid(uid)
    #print('ok! go to action!')
   
    if re.search('dcard_.*', event.message.text, re.IGNORECASE): #set up a button event.message.text == "靠北負評預警": #set up a button
        
        # school = '台灣科技大學'
        # ename = 'ntust'
        # text = 'dcard_ntust_台科大'

        text = event.message.text
        ename = text.split('_')[1]
        school = text.split('_')[2]

        content = Dcardcrawler(school=school, 
                                ename= ename, 
                                ).select_dcard()

        keywordlist = pd.read_csv('keyword_count_main.csv')

        mss =  weight_care_new_json( content  , keywordlist = keywordlist)

        cont = ''
        for i in mss['message']:
            # print(i)
            cont += i

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=cont))

        return 0

    if event.message.text == "dcard負評預警":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='請輸入要查詢的dcard學校，如：dcard_ntust_台科大'))

        return 0

    
    if event.message.text == "社群預警":
        buttons_template = TemplateSendMessage(
            alt_text='常用社群預警',
            template=ButtonsTemplate(
                title='校務上常用社群預警，目前囊括大學生常用的ptt與dcard',
                text='請選擇',
                thumbnail_image_url='https://i.imgur.com/Dt97YFG.png',
                actions=[
                    MessageTemplateAction(
                        label='dcard負評預警',
                        text='dcard負評預警'
                    ),
                    MessageTemplateAction(
                        label='ptt負評預警',
                        text='ptt負評預警'
                    ),
                    MessageTemplateAction(
                        label='靠北負評預警',
                        text='靠北負評預警'
                    ),  
                       MessageTemplateAction(
                           label='同儕學校靠北預警',
                           text='同儕學校靠北預警'
                       )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return 0
    
    
    if event.message.text == "使用說明":
        buttons_template = TemplateSendMessage(
            alt_text='使用說明',
            template=ButtonsTemplate(
                title='IR 小幫手使用說明',
                text='請選擇',
                thumbnail_image_url='https://i.imgur.com/Dt97YFG.png',
                actions=[
                    MessageTemplateAction(
                        label='快速上手',
                        text='快速上手'
                    ),
                    {
                    "type": "uri",
                    "label": "詳細說明手冊",
                    "uri": "https://hackmd.io/s/SJtT1bStf"
                    }   
                            
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)     
        return 0   
    
    if event.message.text == "快速上手":
        url='https://i.imgur.com/3G0hxo4.jpg'
        image_message1 = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        url='https://i.imgur.com/ClOTzLg.jpg'
        image_message2 = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        
        url='https://i.imgur.com/TxrcyjS.jpg'
        image_message3 = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        url='https://i.imgur.com/vaPrStq.jpg'
        image_message4 = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        
        line_bot_api.reply_message(
            event.reply_token, [image_message1,image_message2,
                                image_message3,image_message4])
    
        return 0   
        
    

if __name__ == '__main__':
    app.run()
