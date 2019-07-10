import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlopen
from webdriver_manager.chrome import ChromeDriverManager


# selenium 기본 설정
options = webdriver.ChromeOptions()
options.add_argument('headless')
# user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/91.0.4472.101 Safari/537.36
options.add_argument("--start-maximized")
options.add_argument("--disable-cache")
options.add_argument("--lang=ko_KR")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36")
# headless 로 사용할 경우 user-agent 를 바꿔 줘야한다.
# agent = driver.execute_script("return navigator.userAgent")
options.add_argument("--keep-alive")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
# driver = webdriver.Chrome('/Users/JIN/Documents/programming/chromedriver_win32/chromedriver', options=options)
# 직접 다운로드 하는 방식 https://sites.google.com/chromium.org/driver/home
driver.implicitly_wait(1)


# 첫 페이지 방문
page = 1
driver.get('https://www.sta1.com/shops?gndr=F&shopType=S&pg=%d' % page)
last_height = driver.execute_script("return document.body.scrollHeight")


# 무한 스크롤 페이지의 마지막 페이지 찾기 (NaN)
while True:
    page += 1
    driver.get('https://www.sta1.com/shops?gndr=F&shopType=S&pg=%d' % page)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        page = page - 1
        break

    last_height = new_height


# 크롤링 작업
time.sleep(0.1)
columns = ['store_name', 'age', 'info', 'url', 'instagram', 'sta1_shop_url']
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
content = soup.find(attrs={'class': 'shop-list'})
w_csv = open('./sta1.csv', 'a', encoding='utf-8-sig', newline='')
writer = csv.writer(w_csv)
writer.writerow(columns)
last_i = len(content.find_all('li'))

i = 0
for c in content.find_all('li'):
    data = []
    store_url = ''
    store_link = c.find(attrs={'class': 'wrapper'})
    strong = store_link.find('strong')
    em = store_link.find_all('em')
    try:
        data.append(strong.text)
    except:
        data.append('no_name')
    try:
        data.append(em[0].text)
    except:
        data.append('no_age')
    try:
        data.append(em[1].text)
    except:
        data.append('no_info')
    try:
        url = 'https://www.sta1.com' + str(store_link.attrs['href'])
        result = urlopen(url)
        html = result.read()
        soup = BeautifulSoup(html, 'html.parser')
        x = soup.find('body').find('script').text
        store_url = str(x.split('url:"')[1].split("?")[0]).replace('\\u002F', '/')
        data.append(store_url)
    except:
        print('redirect err')
        data.append('no_url')
    try:
        driver.get(store_url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        x = 0
        temp = []
        for j in range(5):
            x = str(soup).find('instagram.com/', x + 1)
            if x == -1:
                break
            x1 = (str(soup)[x:].split('/')[1].split('"')[0]).replace("#", "").replace("<", "").replace("@", "")
            if (len(x1) > 0) and x1 != 'user' and x1 != 'oauth' and x1 != 'explore' and x1 != 'p' and x1 != 'vp' and x1 != 'v1' and '\n' not in x1 and ')' not in x1 and '?' not in x1:
                temp.append(x1)

        temp = list(set(temp))
        if len(temp) == 0:
            data.append('no_instagram')
        else:
            data.append(','.join(temp))
    except:
        data.append('no_instagram')
    try:
        item_link = c.find(attrs={'class': 'button'})
        data.append('https://www.sta1.com' + str(item_link.attrs['href']))
    except:
        data.append('no_shop_url')
    writer.writerow(data)
    i += 1
    print(i, '/', last_i)

w_csv.close()
driver.close()
driver.quit()
