import time
import requests
import random
import json
import pandas as pd
import datetime
import emoji


def isgdShorter(url):
    '''
    短網址
    '''
    req = requests.get('https://is.gd/create.php?format=simple&url='+str(url))
    content = req.content
    if b'Error' in content:
        content = url

    return content.decode()

  

def weight_care_new_json(news_json, keywordlist = []): 
    '''
    專門計算selenium 從fb爬下來的json計算權重
    '''
    
    keyword = pd.read_csv('keyword_count_main.csv')
    keyword = keyword[['keyword','norm_score']]
    
    # if len(keywordlist) >0:
    #     # 把學校關鍵字加進去
    #     school_keyword = pd.DataFrame({'keyword':keywordlist,'norm_score':[1.0]*len(keywordlist)})
    #     keyword = pd.concat([school_keyword,keyword])
    #     keyword = keyword.drop_duplicates('keyword')
    #     keyword = keyword.reset_index()
    #     keyword = keyword[['keyword','norm_score']]

    #process json to df 以下為皓軒的code
    news_df = pd.DataFrame.from_dict(news_json)
    news_score_list = []
    news_df = news_df[pd.notnull(news_df['message'])]
    news_df= news_df.reset_index(drop=True)
    
    
    for word in news_df['message']:
        keyword_select  = keyword[pd.Series([ gg in word for gg in keyword['keyword'].tolist()])]
        if len(keyword_select) ==0:
            news_score_list.append(0)
        else:
            news_score_list.append(keyword_select['norm_score'].sum())
    
    news_df_weight = pd.concat([  news_df, pd.DataFrame(news_score_list, columns = ['weight'])], axis = 1)
    news_df_weight= news_df_weight.sort_values(['weight'], ascending = False)
    

    news_df_weight = news_df_weight[news_df_weight['weight']!=0]
    
    if len(news_df_weight)<=0:# 代表有所有文章沒有出現任何 在keyword_count_main 中的文字

        return ''
    
    # 把權重根據5等份轉換成星號到weight_rank
    news_df_weight['weight_rank']=pd.cut(news_df_weight['weight'], 4, labels=[':star:',':star:'+':star:',':star:'+':star:'+':star:',':star:'+':star:'+':star:'+':star:'])
    
    # make content
    
    content_list= []
    for index, row in news_df_weight.iterrows():
        content = ""
        # 處理時間
        # tmpt = datetime.datetime.now()
        # ts = row['timestamp']
        # print(ts)
        # date = datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        # '2020-' + row['timestamp'].replace('月','-').replace('日.*','-')
        
        #如果是在一天內的文章
        try:
            link = isgdShorter(row['link'])
        except:
            link=row['link']
        
        chars_per_line = 50
        title = ''
        for a in range(0, len(row.get('message')), chars_per_line):
            title=str(row.get('message')[0:50]) + str(r'...(全文請見下方連結)')
            title=title.replace('\n\n','\n')
        
        # 'created_time' changed to simple format
        ceated_time  = str(row['timestamp'])
        content += '標題 = {}\n關注指數 = {}\nLink = {}\nDate = {}\n\n'.format(
                title, 
                #round(row['weight'] ,2),
                emoji.emojize(row['weight_rank'],use_aliases=True ),
                link,
                ceated_time,
                )
        content_list.append(content)



    news_df_weight['message'] = content_list
    return news_df_weight



class Dcardcrawler:
    def __init__(self, school, ename= 'NTU', keywordlist = []):
        self.school=school
        self.ename= ename
        self.keywordlist = keywordlist
        
        #元培在dcard名子不一樣，因此要另外修改
        if ename == 'YUMT':
            self.ename_lower = 'ypu'
        else:
            self.ename_lower = ename.lower()
        # 改使用 API 方式
        self.header = {'authority': 'www.dcard.tw',
                        'method': 'GET',
                        'path': '/_api/forums/' + self.ename_lower +'/posts?popular=false&limit=30',
                        'scheme': 'https',
                        'accept': 'application/json',
                        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-CN;q=0.5',
                        'cookie': '__cfduid=d504aeae9a440cd7203f85f731467be0f1547526562; _ga=GA1.2.451511484.1547526564; __auc=e97f7be41684fc569db1811e5bb; __gads=ID=4550f45ddfb5ca38:T=1547526565:S=ALNI_Ma5zMgCV0epLrUAeQWgeStOkVYDzQ; _atrk_siteuid=yaRu7petUS8Nw1KD; _fbp=fb.1.1549942898388.585175892; dcard=eyJ0b2tlbiI6IjlWemw1b2hZUlJXOTVRSERmY0lFZUE9PSJ9; dcard.sig=H3nXXxV2G3-Sm2MEWknZ7L1HMnY; G_ENABLED_IDPS=google; _fbc=fb.1.1557714992745.IwAR16gXlGLm6soQA_EwUQRKRrD16b5QtbRVST6xjL2TywLrR0LE-Z9OArkV8; cf_clearance=8adf4067ad2681ea1406260fb2c7f0aa0c17f5bf-1559721181-1800-250; dcsrd=uY8fSKpkzGIiUrEQIsr_RgEK; dcsrd.sig=p922Dw18jIm9oh2PPbp_8GgUWWA; _gid=GA1.2.1192734338.1559721495; __asc=d267ae3a16b26a5482a02c9392b; amplitude_id_bfb03c251442ee56c07f655053aba20fdcard.tw=eyJkZXZpY2VJZCI6ImRiMzQ5MGVhLTc4MmUtNDIwZC1hMjkxLWFhYzk3ODMxMjJkYlIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTU1OTcyMTQ5NTI3OSwibGFzdEV2ZW50VGltZSI6MTU1OTcyMTQ5NTI3OSwiZXZlbnRJZCI6MCwiaWRlbnRpZnlJZCI6MCwic2VxdWVuY2VOdW1iZXIiOjB9',
                        'referer': 'https://www.dcard.tw/_api/forums/' + self.ename_lower +'/posts?popular=false&limit=30',
                        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'}
    # Dcard爬蟲主程式
    def select_dcard(self):
        #因為現在dcard有機器人驗證，因此爬蟲不能太頻繁
        time.sleep(random.randint(10,11))
        
        dom = requests.get('https://www.dcard.tw/_api/forums/' + self.ename_lower +'/posts?popular=false&limit=30',headers = self.header)
        # try:
        reJson = pd.DataFrame(json.loads(dom.text))
        ##### 創造出重要性分析需要的欄位 #####
        reJson.rename(columns={'excerpt':'message'}, inplace = True) # 修改欄位名稱
        # 創造出連結，待會重要性分析會把他轉短網址
        reJson['link'] = 'https://www.dcard.tw/f/' + self.ename + '/p/'+ reJson['id'].astype(str)
        #將資料時間轉時間型態，因為是utc時間，轉成現在時間要+8小時
        reJson['datetime'] = pd.to_datetime(reJson['createdAt'].str[:-1]) + datetime.timedelta(hours=8)
        
        #計算24小時前的時間
        hour_24ago = datetime.datetime.now() - datetime.timedelta(days=1) 
        #先過濾掉以前的資料
        reJson = reJson[reJson['datetime'] >hour_24ago]
        # 重要性分析需要這個資料，這個時間基本上沒有意義，只是為了讓方法可以執行
        reJson['timestamp'] = time.time()
        
        
        # 如果到這還有資料的話
        if not reJson.empty:
            return reJson
        else:
            return ''
              
        # except:
        #     print(self.school +' 被機器人驗證擋下來了')
        #     return ''


# school = '台灣科技大學' #可以變動，可放入mangodB
# ename = 'ntust' #網址需要

# 'https://www.dcard.tw/_api/forums/' + ename +'/posts?popular=false&limit=30'

# content = Dcardcrawler(school=school, 
#                         ename= ename, 
#                         ).select_dcard()

# keywordlist = pd.read_csv('keyword_count_main.csv')

# mss =  weight_care_new_json( content  , keywordlist = keywordlist)




