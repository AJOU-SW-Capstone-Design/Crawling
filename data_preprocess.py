# 데이터 전처리 코드
# 서울특별시 지번 주소 -> data 가공 후 result.csv에 저장
import csv

f1 = open('seoul_address_raw.csv', 'r', encoding='UTF8')
rd = csv.reader(f1)

f2 = open('seoul_address.csv', 'w', newline='', encoding='UTF8')
wr = csv.writer(f2)

for line in rd:
    address = ''
    s = line[0]
    arr = s.split('|')
    if arr[-1] == '0':
        continue
    address = arr[3] + ' ' + arr[4] + ' ' + arr[5]
    if arr[7] == '1':
        address += ' 산'
    address = address + ' ' + arr[8] + '-' + arr[9]
    wr.writerow([address])

f1.close()
f2.close()