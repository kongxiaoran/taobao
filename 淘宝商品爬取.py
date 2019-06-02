from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from pyquery import PyQuery as pq
from config import *
import pymongo
import time

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
# options.add_argument('--headless')
# options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
options.add_argument(r'--user-data-dir=C:\Users\12541\AppData\Local\Google\Chrome\User Data')
# 在程序运行前，注意不能有打开的chrome浏览器
# C:\Users\12541\AppData\Local\Google\Chrome\User Data\Default
# chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\selenum\AutomationProfile"
browser =  webdriver.Chrome(r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe',options=options)  #已将chromedriver.exe放在了  D:\Anaconda3 下，所以可以不直接填路径了
wait = WebDriverWait(browser,10)

def search():
    try:
        browser.get('https://taobao.com/')
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#q'))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input.send_keys(KEYWORD)
        submit.click()
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        get_products()
        return total.text
    except TimeoutException:
        return search()
# mainsrp-pager > div > div > div > div.form > input
#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit
def next_page(page_number):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))
        )
        submit = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span')
                , str(page_number)))
        get_products()
    except TimeoutException:
        next_page(page_number )

def get_products():
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item'))
    )
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image':item.find('.pic .img').attr('src'),
            'price':item.find('.price').text(),
            'deal':item.find('.deal-cnt').text()[:-3]+'人次',
            'title':item.find('.title').text(),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)

def save_to_mongo(result):
    try:
        if db[KEYWORD].insert(result):
            print('储存到MONGODB成功', result)
    except Exception:
        print('储存到MONGODB失败',result)


def main():
    try:
        total = search()
        total = int(re.compile('(\d+)').search(total).group(1))
        # js = 'var aa=document.createElement("DIV");aa.setAttribute("id","mydiv");aa.style.color="#00ff00";' \
        #      'aa.style.fontSize="14px";aa.style.fontWeight="bold";aa.innderHTML="我来过哦";document.body.appendChild(aa);' \
        #      'aa.style.position = "absolute";aa.style.left = "50px";aa.style.top = "0px";aa.style.zIndex = 9999'
        # browser.execute_script(js)
        for i in range(2, total + 1):
            next_page(i)
            time.sleep(10)
    finally:
        browser.close()
        print('抓取结束')


if __name__ == '__main__':
    main()

