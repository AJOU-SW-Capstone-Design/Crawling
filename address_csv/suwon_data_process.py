# 0421 update - 데이터 전처리 코드
# 수원시 영통구 주소만!
import csv

f1 = open('gyeonggi_address_raw.csv', 'r', encoding='UTF8')
rd = csv.reader(f1)

f2 = open('gyeonggi_suwon_address.csv', 'w', newline='', encoding='UTF8')
wr = csv.writer(f2)

address_lst = []
for line in rd:
    address = ''
    s = line[0]
    if s.find('영통구') == -1:
        continue
    arr = s.split('|')
    if arr[-1] == '0':
        continue
    address = arr[3] + ' ' + arr[4] + ' ' + arr[5]
    if arr[7] == '1':
        address += ' 산'
    address = address + ' ' + arr[8] + '-' + arr[9]
    if address in address_lst:
        continue
    address_lst.append(address)
    wr.writerow([address])

f1.close()
f2.close()