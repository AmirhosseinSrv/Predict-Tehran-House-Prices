import re
from bs4 import BeautifulSoup
import requests
import mysql.connector
from sklearn import tree
import math

def Convert(string: str) -> int:
    out = ''
    for ch in string:
        out += str(ord(ch) % 10)
    return int(out)


cnx = mysql.connector.connect(user='Amirhossein', password='',
                              host='127.0.0.1',
                              database='project')

cursor = cnx.cursor()
query = 'CREATE TABLE IF NOT EXISTS Tehran_Homes_Information (area VARCHAR(30) , meters INT , price INT);'
cursor.execute(query)
inp = input('This program will predict home prices in Tehran so Please enter Area and Meter in one line (From Tehran Only) and wait a couple of minutes!\nFor example:saadatabad,resalat,enghelab,niavaran,...: ').split()
inp_area = inp[0]
inp_meter = int(inp[1])
x = []
y = []
int_counter_page = 1
counter_page = str(int_counter_page)
counter_items = 0
counter_items_in_page = 0
while 1:
    request = requests.get('https://www.ihome.ir/en/tehran/property-for-sale-in-' + inp_area + '/' + counter_page + '/')
    soup = BeautifulSoup(request.text,'html.parser')
    find_items = soup.find_all('a',attrs={'class' : 'block'})
    test = ""
    for item in find_items:
        if str(item).find('for-sale') >= 0 and re.search(r'href=\"([\w\/\:\.\-]+)\"',str(item)).group(1) != test:
            second_request = requests.get(re.search(r'href=\"([\w\/\:\.\-]+)\"',str(item)).group(1))
            test = re.search(r'href=\"([\w\/\:\.\-]+)\"',str(item)).group(1)
            second_soup = BeautifulSoup(second_request.text,'html.parser')
            find_price = second_soup.find('div',attrs={'class':'price'})
            find_all_meters = second_soup.find_all('span')
            for meter in find_all_meters:
                if str(meter).find('Square Meters') >= 0:
                    find_meter = meter
                    break
            find_area_split = re.search(r'href=\"([\w\/\:\.\-]+)\"',str(item)).group(1).split('/')
            find_area = find_area_split[7]
            find_meter_int = int(find_meter.text[:find_meter.text.find('S')].strip().replace(',',''))
            if find_price.text.split('\n')[2].strip().replace(',','') == '':
                continue
            find_price_int = int(find_price.text.split('\n')[2].strip().replace(',',''))
            cursor.execute('INSERT INTO Tehran_Homes_Information VALUES (\'%s\',\'%i\',\'%i\');' % (find_area,find_meter_int,int(find_price_int / pow(10,3))))
            cnx.commit()
            counter_items += 1
            counter_items_in_page += 1
            if counter_items == 100 :
                break
    if counter_items == 100 :
        break
    if counter_items_in_page == 24:
        counter_items_in_page = 0
        int_counter_page += 1
        counter_page = str(int_counter_page)
query = 'SELECT * FROM Tehran_Homes_Information;'
cursor.execute(query)
for (area, meters, price) in cursor:
    area_int_data = Convert(area)
    x.append([area_int_data, meters])
    y.append(price)
clf = tree.DecisionTreeClassifier()
clf = clf.fit(x, y)
inp_int_area = Convert(inp_area)
inp_data = [[inp_int_area, inp_meter]]
answer = clf.predict(inp_data) 
print("The program predicts that this home costs:",str(list(answer)[0]) + '000',"Tomans.")
query ='DROP TABLE Tehran_Homes_Information;'
cursor.execute(query)
cnx.close()