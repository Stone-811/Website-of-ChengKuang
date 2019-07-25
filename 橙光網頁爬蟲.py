# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
import time, json, csv, re

'''
#任務日誌
抓取-
男性向: http://www.66rpg.com/pcchannel/t_45/61.shtml
女性向: http://www.66rpg.com/pcchannel/t_45/7.shtml
完結: http://www.66rpg.com/pcchannel/t_45/14.shtml
中性向: http://www.66rpg.com/list/tag/tid/12317
'''
Openfile = open("橙光中性向.csv", "w", newline = '', encoding = 'utf-8-sig')
OpenWriter = csv.writer(Openfile)

#設置headers
head = {}
head['User-Agent'] = 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19'

#抓出分類的所有遊戲網址
def GET_GAMES_PAGE(RPGFrontPageUrl):
    
    Browser = webdriver.Firefox()
    Browser.get(RPGFrontPageUrl)
    #Browser.manage().timeouts().pageLoadTimeout(2, TimeUnit.SECONDS)
    time.sleep(3)
    RPGGameSoup = BeautifulSoup(Browser.page_source, 'html5lib')
    #抓取各個遊戲的網址
    Getwebsite = RPGGameSoup.findAll('ul', class_="fl flower_game ")
    print(Getwebsite)
    Get = Getwebsite[1].findAll('li', class_='fl game_size_tiny')
    GameUrlLists = []
    for j in Get:
        #遊戲網址
        GameUrl = j.find('a', href = True)['href']
        GameUrl ="http://www.66rpg.com" + GameUrl
        #print(GameUrl)
        GameUrlLists.append(GameUrl)
        #print(GameUrl)
    Browser.quit()
    print(len(GameUrlLists))
    return GET_GAMES_DATA(GameUrlLists)
    
#抓出遊戲網址內的
def GET_GAMES_DATA(GameUrlLists):
    
    for i in GameUrlLists:
        GameIntroductionDic = {}
        Data = []
        DataCategoryLists = []
        DataBasicLists = []
        DataUpdateLists = []
        Browser = webdriver.Firefox()
        #遊戲ID
        GameID = i.split('game/')[1]
        Browser.get(i)
        time.sleep(2)
        #Browser.manage().timeouts().pageLoadTimeout(2, TimeUnit.SECONDS)
        GamesPageSoup = BeautifulSoup(Browser.page_source, 'html5lib')
        #遊戲介紹
        GameIntroduction = GamesPageSoup.find('div', class_="content game_des_content")
        Data.append(GameIntroduction)
        #分類標籤
        try:
            Category = GamesPageSoup.find('div', class_='tags')
            CategoryData = Category.findAll('a', href = True)
            for i in CategoryData:
                DataCategoryLists.append(i.text)
        except:
            DataCategoryLists.append("None")
            
        #基本資料 - 作品人氣、鮮花、字數、分享、點讚、收藏、發布時間、最後更新時間
        try:
            Basic = GamesPageSoup.find("div", class_= "statistics")
            Label = Basic.findAll('span', class_='fl')
            Value = Basic.findAll('span', class_='fr')
            for i, j in zip(Label, Value):
                dataBasic = str(i.text.strip()) + ':' + str(j.text.strip())
                DataBasicLists.append(dataBasic)
        except:
            DataBasicLists.append("None")
            
        #更新紀錄
        try:
            Update = GamesPageSoup.find('div', class_='content update_log_content')
            UpdateDate = Update.findAll('span', class_='date')
            UpdateTxt = Update.findAll('span', class_='txt')
            for i, j in zip(UpdateDate, UpdateTxt):
                dataUpdate = str(i.text.strip()) + ':' + str(j.text.strip())
                DataUpdateLists.append(dataUpdate)    
        except:
            DataUpdateLists.append("None")
        #抓取留言紀錄
        #使用python regular expression
        #使用該遊戲時間長短格式
        MinsTimeRe = re.compile(r'\d+分钟')
        HoursTimeRe = re.compile(r'\d+小时')
        #留言時間格式
        DateRe = re.compile(r'\d+-\d\d-\d\d')
        #//*[@id="comment"]/div[3]/div[1]/div[3]/div[2]/div[3]/div[1]/span[2]
        #//*[@id="comment"]/div[3]/div[1]/div[4]/div[2]/div[3]/div[1]/span[2]
        DateLists = []
        DateDics = {}
        try:
            MaxPage = GamesPageSoup.find("li", class_= "last")['data-page']
            if int(MaxPage) >= 50:
                MaxPage = 50
            PageCount = 1
            for i in range(2, int(MaxPage)+1):########################
                #組織Xpath
                Element1 = '//*[@id="comment"]/div[3]/div[2]/ul/li['
                PageCount = PageCount + 1
                if int(i) >=7:
                    PageCount = 7
                Str = str(PageCount)
                Element2 = ']'
                Element = Element1 + Str + Element2
                try:
                    ClickSomething = Browser.find_element_by_xpath(Element)
                    ClickSomething.click()
                    time.sleep(3)########################
                    #Browser.manage().timeouts().pageLoadTimeout(2, TimeUnit.SECONDS)
                    GamesPageSoup = BeautifulSoup(Browser.page_source, 'html5lib')
                    Comments = GamesPageSoup.find("div", class_="all-comment-box")
                    UserInfo = Comments.findAll("div", class_= "item")#user-info 
                    for user in UserInfo:
                        DateInfoStr = ""
                        for i in user.find("div", class_= "fl").findAll("span"):
                            DateInfoStr = DateInfoStr + str(i.text)
                        print(DateInfoStr)
                        DateInfo = DateRe.search(DateInfoStr)
                        DateInfo = DateInfo.group(0)
                        DateLists.append(DateInfo)
                except:
                    DateLists.append("None")
                print(DateLists)
        except:
            DateLists = ['None']
        for DLists in DateLists:
            if DLists not in DateDics:
                DateDics[DLists] = 1
            elif DLists in DateDics:
                DateDics[DLists] += 1
                
        AllData = [GameID, DataCategoryLists, DataBasicLists, DataUpdateLists, DateLists, DateDics]
        OpenWriter.writerow(AllData)
        print(AllData)    
        #GameIntroductionDic[GameID] = [Data]
        #OpenWriter.writerow(AllData)  寫入AllData
        Browser.quit()
    return AllData

Target = "http://www.66rpg.com/list/tag/tid/12317"
GET_GAMES_PAGE(Target)

Openfile.close()
