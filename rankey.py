import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


# selenium 기본 설정
options = webdriver.ChromeOptions()
options.add_argument('headless')
# user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/91.0.4472.101 Safari/537.36
options.add_argument("--start-maximized")
options.add_argument("--disable-cache")
options.add_argument("--lang=ko_KR")
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36")
# headless 로 사용할 경우 user-agent 를 바꿔 줘야한다.
# agent = driver.execute_script("return navigator.userAgent")
options.add_argument("--keep-alive")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
# driver = webdriver.Chrome('/Users/JIN/Documents/programming/chromedriver_win32/chromedriver', options=options)
# 직접 다운로드 하는 방식 https://sites.google.com/chromium.org/driver/home
driver.implicitly_wait(0.1)


# csv 저장 파일 열기
columns = ['store_name', 'url', 'instagram']
with open('./rankey.txt', 'r', encoding='utf-8') as f:
    url_list = [[str(url.split('http')[0]), str(url.split('?site_url=')[-1]).replace("\n", "")]
                for url in f.readlines()]

w_csv = open('./rankey.csv', 'a', encoding='utf-8-sig', newline='')
writer = csv.writer(w_csv)
writer.writerow(columns)


# 크롤링 작업
i = 0
last_i = len(url_list)
for name_url_link in url_list:
    data = [name_url_link[0], name_url_link[1]]
    try:
        driver.get("http://"+name_url_link[1])
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
            if (
                    len(x1) > 0) and x1 != 'user' and x1 != 'oauth' and x1 != 'explore' and x1 != 'p' and x1 != 'vp' and x1 != 'v1' and '\n' not in x1 and ')' not in x1 and '?' not in x1:
                temp.append(x1)

        temp = list(set(temp))
        if len(temp) == 0:
            data.append('no_instagram')
        else:
            data.append(','.join(temp))

    except:
        print('err', name_url_link[0])
        data.append("can not load")

    writer.writerow(data)
    i += 1
    print(i, '/', last_i)


w_csv.close()
driver.close()
driver.quit()
