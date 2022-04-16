import csv
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

import database as db

# 추후 크롤링을 위한 data 저장
rest_crawled_infos = []

# 도로명 주소 data > address list에 저장
address = []
f = open('seoul_address.csv', 'r', encoding='UTF8')
rd = csv.reader(f)

for line in rd:
    address.append(line[0])

f.close()

# 요기요 사이트 접속
driver = webdriver.Chrome('chromedriver.exe')
url = "https://www.yogiyo.co.kr/"
driver.get(url)
driver.maximize_window()
time.sleep(2)

# 검색창 선택
xpath = '''//*[@id="search"]/div/form/input'''
element = driver.find_element_by_xpath(xpath)
time.sleep(2)

# 음식 카테고리 리스트
category_lst = ['치킨', '피자양식', '중식', '한식', '일식돈까스', '족발보쌈', '야식', '분식', '카페디저트', '편의점']

for a in address:
    element.clear()
    # 검색창 입력
    element.send_keys(a)
    time.sleep(2)

    # 조회버튼 클릭
    search_xpath = '''//*[@id="button_search_address"]/button[2]'''
    driver.find_element_by_xpath(search_xpath).click()
    time.sleep(3)

    try:
        # 주소 검색 결과 없으면 해당 주소 pass
        no_result_xpath = '//*[@id="search"]/div/form/ul/li[1]'
        no_result = driver.find_element_by_xpath(no_result_xpath)
        time.sleep(2)
        continue
    except NoSuchElementException:
        time.sleep(2)
        pass

    # 카테고리 별 조회
    cur_url = driver.current_url
    for category in category_lst:
        category_url = ''
        category_url = cur_url + category + '/'
        driver.get(category_url)
        time.sleep(2)

        # 스크롤 제어
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)") # 스크롤을 가장 아래로 내린다
        # time.sleep(5)
        # pre_height = driver.execute_script("return document.body.scrollHeight") # 현재 스크롤 위치 저장

        # while True :
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")  # 스크롤을 가장 아래로 내린다
        #     time.sleep(10)
        #     cur_height = driver.execute_script("return document.body.scrollHeight")  # 현재 스크롤을 저장한다.
        #     if pre_height == cur_height :
        #         break
        #     else:
        #         pre_height = driver.execute_script("return document.body.scrollHeight")

        # time.sleep(5)

        # 식당 클릭
        index = 1
        while True:
            try:
                rest_xpath = '//*[@id="content"]/div/div[4]/div/div[2]/div[' + str(index) + ']/div'
                driver.find_element_by_xpath(rest_xpath).click()
                time.sleep(5)

                # 페이지 소스 출력
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                # 식당 상세정보 크롤링 (r_name, min_price, order_fee)
                
                raw_discount_info = soup.select_one('#content > div.restaurant-detail.row.ng-scope > div.col-sm-8 > div.restaurant-info > div.restaurant-content > ul > li.discount-desc > span')
                raw_r_name = soup.select_one('#content > div.restaurant-detail.row.ng-scope > div.col-sm-8 > div.restaurant-info > div.restaurant-title > span')
                raw_min_price = soup.select_one('#content > div.restaurant-detail.row.ng-scope > div.col-sm-8 > div.restaurant-info > div.restaurant-content > ul > li:nth-child(3) > span')
                raw_order_fee = soup.select_one('#content > div.restaurant-detail.row.ng-scope > div.col-sm-4.hidden-xs.restaurant-cart > ng-include > div > div.cart > div:nth-child(5) > span.list-group-item.clearfix.text-right.ng-binding')
                
                discount_info = raw_discount_info.get_text()
                r_name = raw_r_name.get_text()
                min_price = raw_min_price.get_text().replace(',', '').replace('원', '')
                order_fee = raw_order_fee.get_text().split('배달요금 ')[1].split('원')[0].replace(',', '')
        
                rest_crawled_info = {
                    "r_name": r_name, 
                    "category": category, 
                    "min_price": min_price, 
                    "order_fee": '(0,' + order_fee + ')',
                    "r_location": a
                }
                rest_crawled_infos.append(rest_crawled_info)
                driver.back()
                time.sleep(5)
            except NoSuchElementException:
                break
            if index == 2:
                break
            index += 1

driver.close() # 크롬드라이버 종료

# rest_crawled_infos 리스트에 담긴 rest 정보 db에 저장
# INSERT INTO post (title, order_time, post_time, shooting_user, p_location, u_id, r_id) VALUES (
for info in rest_crawled_infos:
    sql = 'INSERT INTO restaurant (r_name, category, min_price, order_fee, r_location) VALUES ("'
    sql = sql + info["r_name"] + '", "' + info["category"] + '", ' + info["min_price"] + ', "' + info["order_fee"] + '", "' + info["r_location"] + '")'
db.execute('insert', sql)