
import time

import requests

import random

import json

import pandas as pd

import datetime



def dcard_board( ename, limit):

    # 設定爬蟲參數

    header = {'authority': 'www.dcard.tw',

                            'method': 'GET'}

    dom = requests.get('https://www.dcard.tw/_api/forums/' + ename +'/posts?popular=false'+'&limit=' + str(limit), headers = header)



    reJson = pd.DataFrame(json.loads(dom.text))



    ##### 更改欄位名稱 #####

    reJson =reJson.rename(columns={'excerpt':'message'}) # 修改欄位名稱



    # 創造出連結

    reJson['link'] = 'https://www.dcard.tw/f/' + ename + '/p/'+ reJson['id'].astype(str)



    #將資料時間轉時間型態，因為是utc時間，轉成現在時間要+8小時

    reJson['createdAt'] = pd.to_datetime(reJson['createdAt'].str[:-1]) + datetime.timedelta(hours=8)

    

    reJson = reJson[['id', 'title', 'likeCount','createdAt','forumName','link']]

    

    reJson.columns = ['ID', '標題', '心情數', '時間', '看板','資料來源網址']



    # reJson.to_csv('Dcard_版位爬蟲_' + reJson['看板'].iloc[0] + '.csv', encoding='utf-8-sig')





    return reJson

    

import cloudscraper

import json

import math

import time

import random

import re

scraper = cloudscraper.create_scraper()



def dcard_keyword( word = '台科大', limit=30):

    # 設定爬蟲參數

    headers = {'authority': 'www.dcard.tw',

                        'method': 'GET',

                        'scheme': 'https',

                        'accept': 'application/json',

                        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-CN;q=0.5',

                        'cookie': '__cfduid=d504aeae9a440cd7203f85f731467be0f1547526562; _ga=GA1.2.451511484.1547526564; __auc=e97f7be41684fc569db1811e5bb; __gads=ID=4550f45ddfb5ca38:T=1547526565:S=ALNI_Ma5zMgCV0epLrUAeQWgeStOkVYDzQ; _atrk_siteuid=yaRu7petUS8Nw1KD; _fbp=fb.1.1549942898388.585175892; dcard=eyJ0b2tlbiI6IjlWemw1b2hZUlJXOTVRSERmY0lFZUE9PSJ9; dcard.sig=H3nXXxV2G3-Sm2MEWknZ7L1HMnY; G_ENABLED_IDPS=google; _fbc=fb.1.1557714992745.IwAR16gXlGLm6soQA_EwUQRKRrD16b5QtbRVST6xjL2TywLrR0LE-Z9OArkV8; cf_clearance=8adf4067ad2681ea1406260fb2c7f0aa0c17f5bf-1559721181-1800-250; dcsrd=uY8fSKpkzGIiUrEQIsr_RgEK; dcsrd.sig=p922Dw18jIm9oh2PPbp_8GgUWWA; _gid=GA1.2.1192734338.1559721495; __asc=d267ae3a16b26a5482a02c9392b; amplitude_id_bfb03c251442ee56c07f655053aba20fdcard.tw=eyJkZXZpY2VJZCI6ImRiMzQ5MGVhLTc4MmUtNDIwZC1hMjkxLWFhYzk3ODMxMjJkYlIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTU1OTcyMTQ5NTI3OSwibGFzdEV2ZW50VGltZSI6MTU1OTcyMTQ5NTI3OSwiZXZlbnRJZCI6MCwiaWRlbnRpZnlJZCI6MCwic2VxdWVuY2VOdW1iZXIiOjB9',

                        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'}



    url = 'https://www.dcard.tw/_api/search/posts?query=' + word + '&limit='+str(limit)

    req = scraper.get(url, headers = headers)

    js = json.loads(req.text)

    dcard_keyword = pd.DataFrame(js)



    #-------指定論壇的文章內容 - 抓取文章內容---------

    dcard_postjs_df = []

    for id in dcard_keyword['id']:

        time.sleep(random.randint(1, 4))

        posturl = 'https://www.dcard.tw/_api/posts/' + str(id)

        postreq = requests.get(posturl)

        postjs = json.loads(postreq.text)

        dcard_postjs = pd.DataFrame([postjs])

        dcard_postjs['link'] = 'https://www.dcard.tw/f/' + 'stock' + '/p/'+ str(id)

        dcard_postjs_df.append(dcard_postjs)



    dcard_postjs_df = pd.concat(dcard_postjs_df)

    dcard_postjs_df = dcard_postjs_df[['id', 'title', 'content', 'likeCount','createdAt','forumName','link']]

    dcard_postjs_df.columns = ['ID', '標題', '內文', '心情數', '時間', '看板','資料來源網址']

    #將資料時間轉時間型態，因為是utc時間，轉成現在時間要+8小時

    dcard_postjs_df['時間'] = pd.to_datetime(dcard_postjs_df['時間'].str[:-1]) + datetime.timedelta(hours=8)

    # dcard_postjs_df.to_csv('Dcard_'+word +'_文章內容.csv' , encoding= 'utf-8-sig')



    #-------抓取文章留言內容-------



    # com_js_df_all = []

    # for id in dcard_postjs_df['ID']:

    #     commenturl = 'https://www.dcard.tw/_api/posts/'+ str(id) + '/comments'

    #     com_req = requests.get(commenturl)

    #     com_js = json.loads(com_req.text)



    #     if len(com_js)!=0:

            

    #         # 抓出原文標題

    #         dcard_postjs_df_tmp = dcard_postjs_df[dcard_postjs_df['ID'] == id ]

    #         com_js_df = pd.DataFrame(com_js)

    #         com_js_df['標題'] = dcard_postjs_df_tmp['標題'].iloc[0]

    #         com_js_df['留言網址'] = 'https://www.dcard.tw/f/stock/p/' + com_js_df['postId'].astype(str) + '/b/' + com_js_df['floor'].astype(str)

    #         com_js_df_all.append(com_js_df)



    # com_js_df_all  = pd.concat(com_js_df_all)

    # com_js_df_all = com_js_df_all[['標題','content', 'likeCount','createdAt','留言網址' ]]

    # com_js_df_all.columns = ['標題', '留言','心情數','時間','留言網址']

    # #將資料時間轉時間型態，因為是utc時間，轉成現在時間要+8小時

    # com_js_df_all['時間'] = pd.to_datetime(com_js_df_all['時間'].str[:-1]) + datetime.timedelta(hours=8)

    # com_js_df_all.to_csv('Dcard_'+word +'_文章留言內容.csv' , encoding= 'utf-8-sig')

    return dcard_postjs_df #, com_js_df_all



