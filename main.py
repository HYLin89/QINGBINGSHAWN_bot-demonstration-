
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions   #20230623新增
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import pandas as pd
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium import webdriver
import random as rd
import re
from selenium.webdriver.common.by import By
import json

os.chdir(r'C:\Users\Hylin\Desktop\projv0')

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--window-size=1280,800")



browser = webdriver.Chrome(options=chrome_options)
browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """
})



url=f'https://icook.tw/search/家常菜/'

browser.get(url)
browser.implicitly_wait(20)

df=pd.DataFrame(columns=['食譜','url','食材'])
x=0
pg=4


browser.execute_script("window.scrollBy(0,785);") 

while x<=500:
    
    for i in range(2,25):
        try:
            check=browser.find_element(By.XPATH,'/html/body/div[1]/div[4]/div[2]/main/ul/div/button').click()
            time.sleep(rd.uniform(0.5,1.5))
            try:
                title=browser.find_element(By.XPATH,f'/html/body/div[1]/div[4]/div[2]/main/ul/li[{i}]/a/article/div[2]/div/h2').text
                title=re.sub(r'\/( )*\w+','',title)
                url=browser.find_element(By.XPATH,f'/html/body/div[1]/div[4]/div[2]/main/ul/li[{i}]/a').get_attribute('href')
                ingredients=browser.find_element(By.XPATH,f'/html/body/div[1]/div[4]/div[2]/main/ul/li[{i}]/a/article/div[2]/div/p').text
                ingredients=re.sub(r'食材：','',ingredients)
                
                time.sleep(0.5)

                df.loc[x]=[title,url,ingredients]
                x+=1
                print(title,x)
                browser.execute_script('window.scrollBy(0,120)')
                browser.implicitly_wait(5)
            except:
                continue

        except :
            try:
                title=browser.find_element(By.XPATH,f'/html/body/div[1]/div[4]/div[2]/main/ul/li[{i}]/a/article/div[2]/div/h2').text
                title=re.sub(r'(\/( )*\w+)','',title)           
                url=browser.find_element(By.XPATH,f'/html/body/div[1]/div[4]/div[2]/main/ul/li[{i}]/a').get_attribute('href')
                ingredients=browser.find_element(By.XPATH,f'/html/body/div[1]/div[4]/div[2]/main/ul/li[{i}]/a/article/div[2]/div/p').text
                ingredients=re.sub(r'食材：','',ingredients)
                
                time.sleep(0.5)
                
                df.loc[x]=[title,url,ingredients]
                x+=1
                print(title,x)
                browser.execute_script('window.scrollBy(0,120)')
                browser.implicitly_wait(5)
            except:
                continue

    if (pg<8):
        pg+=1
    else:
        pg=9
    browser.execute_script("window.scrollTo(0,1000);")
    try:
        mousePos=browser.find_element(By.XPATH,f'/html/body/div[1]/div[4]/div[2]/main/nav[2]/ul/li[{pg}]/a').click()
    except:
        pg+=1
        mousePos=browser.find_element(By.XPATH,f'/html/body/div[1]/div[4]/div[2]/main/nav[2]/ul/li[{pg}]/a').click()
    time.sleep(2)




tojson=df.to_json('recipes.json',index=False,orient='records',force_ascii=False)

# browser.close() #關閉虛擬瀏覽器




