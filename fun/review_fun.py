import os
import re
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup as Soup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

# driver_path = os.getcwd() + '\\chromedriver'
# search= "永和區 合作金庫"
# review_page_scroll =1

def google_review_reviews(
    search= "大安區 星巴克", review_page_scroll =3):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless") #無頭模式
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)



    # 設定工作目錄
    # 設定要前往的網址
    url = 'https://www.google.com.tw/maps?hl=zh-TW&tab=rl&authuser=0'  

    # 透過 Browser Driver 開啟 Chrome
    # browser = webdriver.Chrome(driver_path)  
    # r('C:\Users\user\Desktop\合庫\合庫_09_監控機器人的申請與系統建置與數據庫的建置與實際操作\01_監控機器人的申請與系統建置\01_Line推播教學\fun')
    # 透過 Browser Driver 開啟 Chrome
    # browser = webdriver.Chrome('chromedriver')  
    # 前往該網址
    browser.get(url) 

    # 等待到searchbox出現後才繼續往下走~！
    WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'tactile-searchbox-input')))


    # browser.find_elements_by_class_name('tactile-searchbox-input')

    # 網頁元素定位 
    search_input = browser.find_elements_by_class_name('tactile-searchbox-input')[0]

    # 輸入搜尋內容 
    search_input.send_keys(search)

    # 搜尋
    time.sleep(3.8)
    WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'searchbox-searchbutton-container')))

    # 網頁元素定位 
    search_click = browser.find_elements_by_class_name('searchbox-searchbutton-container')[0]

    # 點擊搜尋鍵 
    search_click.click()

    # 成功搜尋
    print("Finish Searching!")

    tcb_list =[]
    i = 1 # 第幾個店家
    Next = True
    while Next:

        time.sleep(6.8)
        # 取得網頁元素框架（搜尋結果）
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'section-result')))

        soup = Soup(browser.page_source,"lxml")
        store_frame = soup.find_all(class_="section-result")

        # 找所有店家名稱
        store_name = []
        for stores in store_frame:
            new_store = stores.get('aria-label')
            if (new_store != None) & (new_store not in store_name):
                store_name.append(new_store)
        print("店家名稱：")
        for sn in store_name:
            print(sn)

        for n in range(len(store_name)):
        # n = 0 # 第幾個店家（每20頁會重置數字）
        # 抓個別店家資料
            time.sleep(2.85)
            # WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'section-back-to-list-button.blue-link noprint')))
        
            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'section-result')))

            store_click = browser.find_elements_by_class_name('section-result')[n]
            store_click.click()

            # 點擊查看所有評論
            # 原本的 class name 中存在空格：'allxGeDnJMl__button allxGeDnJMl__button-text'，會讓程式抓不到
            # 所以空格的部分要改成「.」才能成功抓取

            review_click = browser.find_elements_by_class_name('allxGeDnJMl__button.allxGeDnJMl__button-text')

            actions = ActionChains(browser)


            for rc in range(len(review_click)):
                actions.move_to_element(review_click[rc]).perform()
                if "更多評論" in review_click[rc].text:
                    review_click[rc].click()


            # 評論選單
            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'iRxY3GoUYUY__button.gm2-hairline-border.section-action-chip-button')))

            menu_click = browser.find_elements_by_class_name('iRxY3GoUYUY__button.gm2-hairline-border.section-action-chip-button')

            for mc in menu_click:
                if mc.text == "排序":
                    print(mc.text)
                    mc.click()   

            # 選擇評論類型
            data_index = 1 # 最新

            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'action-menu-entry')))


            category_click = browser.find_elements_by_class_name('action-menu-entry')

            print(category_click[data_index].text)

            category_click[data_index].click()

            # 評論分頁下滑
            # 移動到該網頁元素
            # scroll_time = 3 # 看要滑動幾次

            for st in range(review_page_scroll):
                time.sleep(3)
                # WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[2]')))
                pane = browser.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[2]')
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", pane)
                print(st+1,'scroll'*(st+1))
                time.sleep(3.5)



            # 先將所有照片都點開來
            # 因為一則評論中的照片若超過四張，就會被縮減起來，所以把它點擊開來才能加載並抓取
            all_photo = browser.find_elements_by_class_name('section-review-photo')

            for ap in all_photo:
                ap.click()


            all_title_review = []
            all_subtitle_review = []
            all_star_review = []
            all_date_review = []
            all_text_review = []
            all_photo_review = []
            today = datetime.today().strftime("%Y-%m-%d")

                    
            soup = Soup(browser.page_source,"lxml")
            all_reviews = soup.find_all(class_ = 'section-review ripple-container GLOBAL__gm2-body-2')


            
            for ar in all_reviews:
            # ar = all_reviews[0] # 第幾則評論
                ar.find(class_ = "section-review-title").text
                # 評論者名稱
                all_title_review.append(ar.find(class_ = "section-review-title").text)

                # 評論者代稱＆評論數
                try:
                    subtitle_review = ar.find(class_ = "section-review-subtitle").text
                except:
                    subtitle_review = []
                    


                if ' ・' in subtitle_review: 
                    all_subtitle_review.append(subtitle_review)
                elif ' 在地嚮導' in subtitle_review:
                    all_subtitle_review.append(subtitle_review.strip(' 在地嚮導'))
                else:
                    all_subtitle_review.append(subtitle_review)


                # 評論星數
                all_star_review.append(str(ar.find(class_ = "section-review-stars").get('aria-label').strip().strip("顆星")))


                # 評論時間
                all_date_review.append(ar.find(class_ = "section-review-publish-date").text)


                # 評論內容
                all_text_review.append(ar.find(class_ = "section-review-text").text)


                # 評論照片
                photos = ar.find_all(class_ = "section-review-photo")
                photo_urls = []

                for ph in photos:
                    photo_urls.append(ph.get('style').strip('background-image:url(').strip(')'))
                    
                all_photo_review.append(photo_urls)


            # 將所有評論資料存成Data Frame
            reviews = pd.DataFrame({
                'Store':store_name[n],
                'Today':today,
                'Reviewer Title':all_title_review,
                'Reviewer Subtitle':all_subtitle_review,
                'Star Reviews':all_star_review,
                'Date':all_date_review,
                'Text':all_text_review,
                'Photos':all_photo_review
                })

            # 輸出 csv files
            reviews['頁'] = str(review_page_scroll)+ "頁_評論"
            # reviews.to_csv("個別店家評論/"+ str(i) +"_"+ store_name[n] + '_'+ str(review_page_scroll)+ "頁_評論.csv", encoding = 'UTF-8-sig')
            i += 1
            print("個別店家評論/"+ str(i) +"_"+ store_name[n] + '_'+ str(review_page_scroll)+ "頁_評論")
            tcb_list.append(reviews)


            # 點擊返回店家頁面
            time.sleep(2.5)
            print('return to store')

            WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'geoUxComponentsAppbarButtonWrapper')))

            BacktoStore_btn = browser.find_elements_by_class_name('geoUxComponentsAppbarButtonWrapper')[0]

            BacktoStore_btn.click()

            # 點擊返回搜尋結果
            print('return to search result')
            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'section-back-to-list-button.blue-link.noprint')))

            back_btn = browser.find_elements_by_class_name('section-back-to-list-button.blue-link.noprint')[0]
            back_btn.click()

        # 點擊下一頁按鈕
        try:
            WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.ID, 'n7lv7yjyC35__section-pagination-button-next')))
            next_page = browser.find_elements_by_class_name('n7lv7yjyC35__button.noprint')[1]
            next_page.click()
            # Next = True
            print('Next page!')

            try:
                WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'section-no-result-title')))
                gg = browser.find_elements_by_class_name('section-no-result-title')[0]
                print(gg.text)
                # 有發現！
                if gg.text == '找不到任何結果':
                    Next = False
                else:
                    Next = True
            except:
                Next = True

            # time.sleep(2)
        except:
            Next = False
            print('No next page!')

    browser.quit()
    import numpy as np
    reviews = pd.concat(tcb_list)
    reviews['Date_base'] = np.where(reviews['Date'].str.contains('天前'), 1,
          np.where(reviews['Date'].str.contains('月前'), 30,
            np.where(reviews['Date'].str.contains('年前'), 365, 1)))
    reviews = reviews.reset_index()

    reviews['Day_num'] = reviews['Date'].str.extract('(\d+)').astype(int)

    reviews['Day'] = reviews['Day_num']  * reviews['Date_base']

    reviews['Today'] = pd.to_datetime(reviews['Today'])

    from datetime import timedelta
    reviews['Day'] = reviews['Day'].apply(lambda x: pd.Timedelta(x,'days'))
    reviews['Date']  = reviews['Today'] - reviews['Day']

    return reviews