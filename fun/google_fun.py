from GoogleNews import GoogleNews
import pandas as pd

def googlenews_function(keyword = '台積電', language = 'cn', start_date ='2020/12/01', end_date = '2020/12/28'):
    '''
    - 日期
    - 關鍵字
    - 語言
    - 爬幾頁

    '''
    googlenews = GoogleNews()
    googlenews.clear()
    googlenews.set_encode('utf-8')
    googlenews.set_lang(language)

    all_date_start = start_date.split('/')
    start_year = all_date_start[0]
    start_month = all_date_start[1]
    start_day = all_date_start[2]
    all_date_start ='{}/{}/{}'.format(start_month,start_day,start_year)

    
    all_date_end = end_date.split('/')
    end_year = all_date_end[0]
    end_month = all_date_end[1]
    end_day = all_date_end[2]
    all_date_end ='{}/{}/{}'.format(end_month,end_day,end_year)

    googlenews.set_time_range(start = all_date_start, end = all_date_end)

    googlenews.search(keyword)
    data = googlenews.result()
    print("資料總筆數:",len(data)) 
    news = pd.DataFrame(data)
    # news.to_csv("GoogleNews_" + keyword +"_日期" + start_date.replace('/', '-') + '到' +end_date.replace('/', '-')+ ".csv", index= False)
    return news