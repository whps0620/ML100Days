import datetime
import time
import pandas as pd
from datetime import timedelta
import requests
import emoji
import os

from sklearn.preprocessing import MinMaxScaler

def isgdShorter(url):
    '''
    短網址
    '''
    req = requests.get('https://is.gd/create.php?format=simple&url='+str(url))
    content = req.content
    if b'Error' in content:
        content = url

    return content.decode()



# from fun.google_fun import googlenews_function

# import datetime
# today = datetime.date.today()
# yesterday = today- datetime.timedelta(days = 1)

# today1 = today.strftime("%Y/%m/%d")
# yesterday1 = yesterday.strftime("%Y/%m/%d")

# google_df = googlenews_function(keyword = '合庫', language = 'cn', start_date =today1, end_date =yesterday1)
# keyword = pd.read_csv('keyword_count_main.csv', encoding='cp950')
# content_list, news_df = weight_care_new_json(
#             keyword = keyword , 
#             news_df = google_df, 
#             content_name = 'desc', 
#             link_name='link', 
#             time_name = 'datetime',
#             output_name = 'Googlenews_產出')

def weight_care_new_json(keyword, 
                    news_df, content_name, link_name, output_name, time_name): 
    '''
    - keyword：關鍵字表單
    - news_df：納入處理的表單
    - content_name：要處理分析的內容欄位名稱
    - link_name：要處理分析的鏈接名稱
    - time_name：要處理分析的時間名稱

    '''
    
    
    # 將關鍵字表讀入
    
    ms = MinMaxScaler(feature_range=(0.1, 1))
    keyword['norm_score'] = ms.fit_transform( keyword['count'].values.reshape(-1, 1))
    keyword = keyword[['keyword','norm_score']]


    news_df = news_df[pd.notnull(news_df[content_name])]
    news_df= news_df.reset_index(drop=True)


    ## 計算權重
    news_score_list = []
    for word in news_df[content_name]:
        keyword_select  = keyword[pd.Series([ gg in word for gg in keyword['keyword'].tolist()])]
        if len(keyword_select) ==0:
            news_score_list.append(0)
        else:
            news_score_list.append(keyword_select['norm_score'].sum())

    news_df['weight'] = news_score_list

    news_df= news_df.sort_values(['weight'], ascending = False)


    news_df = news_df[news_df['weight']!=0]

    if len(news_df)<=0:
        return '', ''
    else:
        ## 把權重根據5等份轉換成星號到weight_rank
        news_df['weight_rank']=pd.cut(news_df['weight'], 4, labels=[':star:',':star:'+':star:',':star:'+':star:'+':star:',':star:'+':star:'+':star:'+':star:'])
        # news_df2 = news_df.iloc[0:5]
        content_list= []
        for i in range(len(news_df)):
            news_df_tmp = news_df[i:i+1]

            ## 產出短網址
            try:
                link = isgdShorter(news_df_tmp[link_name].iloc[0])
            except:
                link=news_df_tmp[link_name].iloc[0]

            ## 只秀出最多50個字
            title=news_df_tmp[content_name].iloc[0][0:50] + str(r'...(全文請見下方連結)')
            title=title.replace('\n\n','\n')
            title

            ## 製作產出內容
            
            # make content
            content = ''
            ceated_time  = str(news_df_tmp[time_name].iloc[0])
            content += '標題 = {}\n關注指數 = {}\nLink = {}\nDate = {}\n\n'.format(
                    title, 
                    #round(row['weight'] ,2),
                    emoji.emojize(news_df_tmp['weight_rank'].iloc[0], use_aliases=True ),
                    link,
                    ceated_time,
                    )
            content_list.append(content)
        
        news_df['產出'] = content_list
        news_df['關注指數'] = news_df['weight_rank'].apply(lambda x: emoji.emojize(x, use_aliases=True))
        # news_df.to_csv(output_name + '.csv', encoding = 'utf-8-sig')
        return content_list, news_df