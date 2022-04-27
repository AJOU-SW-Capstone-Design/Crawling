import csv
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

import database as db

# 지번 주소 data > address list에 저장
address = []
f = open('./address_csv/gyeonggi_suwon_address.csv', 'r', encoding='UTF8')
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
raw_category_lst = ['치킨', '피자양식', '중식', '한식', '일식돈까스', '족발보쌈', '야식', '분식', '카페디저트', '편의점']
category_lst = ['치킨', '피자/양식', '중식', '한식', '일식/돈까스', '족발/보쌈', '야식', '분식', '카페/디저트', '편의점']

# 0421 update - DB에 존재하는 식당명, 이미 크롤링된 식당명 리스트 저장
restaurants = []
select_sql = "SELECT r_name FROM restaurant"
result = db.execute("select", select_sql)
for r in result:
    restaurants.append(r[0])

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
    for category in raw_category_lst:
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

        # 식당 선택
        count = 1 #delete
        index = 0
        while True:
            index += 1
            # 0421 update - 식당명 이미 DB에 있거나 중복인 경우, 식당명에 지점이 포함되지 않은 경우 제외
            try:
                r_name_xpath = '//*[@id="content"]/div/div[4]/div/div[2]/div[' + str(index) + ']/div/table/tbody/tr/td[2]/div/div[1]'
                r_name = driver.find_element_by_xpath(r_name_xpath).text
                # 식당명이 이미 DB에 있거나, 이미 크롤링된 식당인 경우
                if r_name in restaurants:
                    continue
                # 식당명에 지점이 포함되지 않은 경우
                if r_name[-1] != '점' and r_name.find('-') == -1:
                    continue
            except NoSuchElementException:
                break
            try:
                rest_xpath = '//*[@id="content"]/div/div[4]/div/div[2]/div[' + str(index) + ']/div'
                driver.find_element_by_xpath(rest_xpath).click()
                time.sleep(5)

                # 페이지 소스 출력
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                # 식당 상세정보 크롤링 (r_name, min_price, order_fee)
                raw_r_name = soup.select_one('#content > div.restaurant-detail.row.ng-scope > div.col-sm-8 > div.restaurant-info > div.restaurant-title > span')
                raw_min_price = soup.select_one('#content > div.restaurant-detail.row.ng-scope > div.col-sm-8 > div.restaurant-info > div.restaurant-content > ul > li:nth-child(3) > span')
                raw_order_fee = soup.select_one('#content > div.restaurant-detail.row.ng-scope > div.col-sm-4.hidden-xs.restaurant-cart > ng-include > div > div.cart > div:nth-child(5) > span.list-group-item.clearfix.text-right.ng-binding')
                
                r_name = raw_r_name.get_text()
                min_price = raw_min_price.get_text().replace(',', '').replace('원', '')
                order_fee_origin = raw_order_fee.get_text().split('배달요금 ')[1].split('원')[0].replace(',', '')
                # 0421 update - order_fee _ 주문금액에 따른 배달비 정보 확인
                order_fee_discount = raw_order_fee.get_text().split('(')[1].split('원')[0].replace(',', '')
                if order_fee_discount == '0':
                    order_fee = '(0,' + order_fee_origin + ')'
                else:
                    order_fee = '(0,' + order_fee_origin + '),(' + order_fee_discount + ',0)'
        
                rest_crawled_info = {
                    "r_name": r_name, 
                    "category": category_lst[raw_category_lst.index(category)], 
                    "min_price": min_price, 
                    "order_fee": order_fee
                }
                restaurants.append(r_name) # 0421 update - 이미 크롤링된 식당명 저장 ... for 중복체크
                sql = 'INSERT INTO restaurant (r_name, category, min_price, order_fee) VALUES ("'
                sql = sql + rest_crawled_info["r_name"] + '", "' + rest_crawled_info["category"] + '", ' + rest_crawled_info["min_price"] + ', "' + rest_crawled_info["order_fee"] + '")'
                
                try:
                    db.execute('insert', sql)
                except:
                    print("Except! - " + sql)
                    pass
                count += 1
                driver.back()
                time.sleep(5)
            except:
                break
            # delete
            if count == 2:
                break

driver.close() # 크롬드라이버 종료

'''
Todo
1) try 정리
2) 할인 정보가 두 개 이상인 경우?
3) 주소 검색 안 될 경우
4) count 조건문 없애기
'''