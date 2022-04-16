# Crawling
요기요 사이트 식당 정보 크롤링

## 기술 스택
### Python
Python 기반으로 Crawling 코드 작성
#### 사용 모듈
• Scrapy  
• BeautifulSoup  
• Selenium

### MySQL
Database 관리

## Crawling 구조
### 사전 세팅
• 도로명주소 Data 저장 (출처: 도로명주소 개발자센터 _ https://www.juso.go.kr/addrlink/addressBuildDevNew.do?menu=mainJusoDb)  
• Database 구축 및 연동  

### Crawling 과정
1. 요기요 사이트 접속  
2. Selenium - 입력창에 배달 위치 입력(도로명주소 Data 활용)  
3. 음식 카테고리 크롤링  
4. 카테고리별 식당 조회  
5. 식당 상세 정보(식당명, 최소주문금액, 주문금액에 따른 배달비) 크롤링  
6. 크롤링한 정보 DB에 저장  
