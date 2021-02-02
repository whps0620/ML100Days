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

import time
import requests
import random
import json
import pandas as pd
import datetime
import emoji
from fun.weight_fun import weight_care_new_json
import pandas as pd
from fun.ptt import Board, crawl_ptt_page, crawl_ptt_page_auto, crawl_ptt_page_auto_comment

keyword = pd.read_csv('keyword_count_main.csv', encoding='cp950')

# import mongodb
# import scheduler


# init flask
app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('vFPL8j39qWb8HtHNOZKzlLV1hEVIjjEssSI0EJ61c+P2aGLVAbtEHGBbG6ld+4E5emRL+8u3MBZRSfKQVdi18QeOf/QXoiXhPWXYfTS05w0qKggHlCd2WgHHQovvbKQOZUZOkdo4nt0oeB2SZBT5twdB04t89/1O/w1cDnyilFU=')

# 必須放上自己的Channel Secret
handler = WebhookHandler('1da69efc27acc97eadee26cf142d99b6')

line_bot_api.push_message('U670cd66f86a530b3cd6e08e7c94b2a96', TextSendMessage(text='你可以開始了'))



# for alarm sys from fb app
# 監聽所有來自 /callback 的 Post Request
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
            title='您好～ 我是TCB合庫小幫手',
            text="提供您TCB專門抓取的內容",
            thumbnail_image_url='https://i.imgur.com/aVTdVKH.jpg',
            actions=[
                MessageTemplateAction(
                    label='快速上手',
                    text='快速上手'
                )
            ]
        )
    )
    
    
    

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.message.text:", event.message.text)
    text = event.message.text
    profile = line_bot_api.get_profile(event.source.user_id)
    nameid = profile.display_name
    uid = profile.user_id
    print('nameid:', nameid)
    print('uid:', uid)

    #-------------- ptt 區塊-----------------
    if re.search('PTT輿情資訊', event.message.text, re.IGNORECASE):
        ptt_content = crawl_ptt_page_auto(Board_Name ='Finance' ,
                                    page_num= 1)

        content_list, news_df = weight_care_new_json(
                keyword = keyword , 
                news_df = ptt_content, 
                content_name = '內容', 
                link_name='文章網址來源', 
                time_name = '時間',
                output_name = 'PTT_內容_產出')

        # 轉換成文字內容，方便linebot push
        if len(content_list)!=0:
            content = ''
            for i in content_list:
                print(i)
                content += i


            line_bot_api.push_message(
                    uid,
                    TextSendMessage(text='#---------👇⭐PTT輿情資訊⭐👇---------#\n\n'+content+
                                        '\n\n#---------☝⭐PTT輿情資訊⭐️☝---------#'))
        else:
            line_bot_api.push_message(
                    uid,
                    TextSendMessage(text='目前無最新消息'))

    #-------------- 問題：google news 區塊-----------------
    if re.search('近期新聞輿情資訊', event.message.text, re.IGNORECASE):
        import datetime
        today = datetime.date.today()
        yesterday = today- datetime.timedelta(days = 1)
        
        today1 = today.strftime("%Y/%m/%d")
        yesterday1 = yesterday.strftime("%Y/%m/%d")
 
        google_df = googlenews_function(keyword = '合庫', language = 'cn', start_date =today1, end_date =yesterday1)
 
        content_list, news_df = weight_care_new_json(
            keyword = keyword , 
            news_df = google_df, 
            content_name = 'title', 
            link_name='link', 
            time_name = 'datetime',
            output_name = 'Googlenews_產出')
 
        # 轉換成文字內容，方便linebot push
        if len(content_list)!=0:
            content = ''
            for i in content_list:
                print(i)
                content += i
 
            line_bot_api.push_message(
                    uid,
                    TextSendMessage(text='#---------👇⭐近期新聞輿情資訊⭐👇---------#\n\n'+content+
                                        '\n\n#---------☝⭐近期新聞輿情資訊⭐️☝---------#'))
        else:
            line_bot_api.push_message(
                    uid,
                    TextSendMessage(text='目前無最新消息'))

    #-------------- dcard 區塊-----------------
    if re.search('Dcard輿情資訊', event.message.text, re.IGNORECASE):
            
            # dcard function
            dcard_postjs_df = dcard_keyword( word = '合作金庫', limit=10)
            
            # 輸出模式
            content_list, news_df = weight_care_new_json(
                keyword =keyword , 
                news_df = dcard_postjs_df, 
                content_name = '內文', 
                link_name='資料來源網址', 
                time_name = '時間',
                output_name = 'Dcard_產出_關鍵字內文')
    
            # 轉換成文字內容，方便linebot push
            if len(content_list)!=0:
                content = ''
                for i in content_list:
                    print(i)
                    content += i
    
                line_bot_api.push_message(
                        uid,
                        TextSendMessage(text='#---------👇⭐Dcard輿情資訊⭐👇---------#\n\n'+content+
                                            '\n\n#---------☝⭐Dcard輿情資訊⭐️☝---------#'))
            else:
                line_bot_api.push_message(
                        uid,
                        TextSendMessage(text='目前無最新消息'))

    #--------------til schedule：google review區塊-----------------
    if re.search('Google Review輿情資訊', event.message.text, re.IGNORECASE):
        reviews = google_review_reviews(
                    search= "中和區 合作金庫", review_page_scroll =1)
        for store in reviews['Store'].unique():
            reviews_tmp = reviews[reviews['Store']==store]

        content_list, news_df = weight_care_new_json(
                    keyword =keyword , 
                    news_df = reviews_tmp, 
                    content_name = 'Text', 
                    link_name='Store', 
                    time_name = 'Date',
                    output_name = 'google revew')

        # 轉換成文字內容，方便linebot push
        content = ''
        for i in content_list:
            print(i)
            content += i

        # 推播
        line_bot_api.push_message(lineid,[
                            TextSendMessage(text = '#---------👇⭐Google review' +'【'+store +'】' +'輿情資訊⭐👇---------#'),
                            TextSendMessage(text = content),
                            TextSendMessage(text = '#---------☝⭐Google review' +'【'+store +'】' +'輿情資⭐️☝---------#')
                            ]) 

    if event.message.text == "dcard負評預警":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='請輸入要查詢的dcard學校，如：dcard_ntust_台科大'))

        return 0

    
    if event.message.text == "社群預警":
        buttons_template = TemplateSendMessage(
            alt_text='常用社群預警',
            template=ButtonsTemplate(
                title='tcb合庫小幫手的社群預警',
                text='請選擇',
                thumbnail_image_url='https://i.imgur.com/bdcKYX1.png',
                actions=[

                    MessageTemplateAction(
                        label='PTT輿情資訊',
                        text='PTT輿情資訊'
                    ),
                    MessageTemplateAction(
                        label='近期新聞輿情資訊',
                        text='近期新聞輿情資訊'
                    ),
                    MessageTemplateAction(
                        label='Dcard輿情資訊',
                        text='Dcard輿情資訊'
                    ),
                    MessageTemplateAction(
                        label='Google Review輿情資訊',
                        text='Google Review輿情資訊'
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return 0
    
    
    if event.message.text == "查看網站":
        buttons_template = TemplateSendMessage(
            alt_text='查看網站',
            template=ButtonsTemplate(
                title='合庫小幫手使用說明',
                text='請選擇',
                thumbnail_image_url='https://i.imgur.com/Dt97YFG.png',
                actions=[
                    MessageTemplateAction(
                        label='查看網站',
                        text='查看網站'
                    ),
                    {
                    "type": "uri",
                    "label": "查看網站",
                    "uri": "https://tmrmds.co/tcb-py-training/"
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
    app.run(debug=True)