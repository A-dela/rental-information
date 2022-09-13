import io
import re
from lxml import etree
import csv
from PIL import Image
import requests
import parsel as ps
from bs4 import BeautifulSoup


def get_urls(base_url, begin_pages, end_pages):
    if begin_pages == 1:
        urls = [base_url + 'pg{}/#contentList'.format(str(i)) for i in range(2, end_pages)]
        urls = [base_url + '#contentList'] + urls
    else:
        urls = [base_url + 'pg{}/#contentList'.format(str(i)) for i in range(begin_pages, end_pages)]
    return urls


def get_detail_url(homepage, headers):
    response = requests.get(url=homepage, headers=headers).text
    soup = BeautifulSoup(response, "lxml")
    div_list = soup.find_all('div', class_='content__list--item')
    detail_url = []
    info3_total = []
    for div in div_list:
        item_list = div.find_all('div', class_='content__list--item--main')
        for item in item_list:
            p_list = item.find_all('p', class_='content__list--item--title')
            for p in p_list:
                a = p.find_all('a')[0].get('href')
                detail = "https://su.lianjia.com" + a
                detail_url = detail_url + [detail]
        content_main = div.find('div', class_='content__list--item--main')
        p_title = content_main.find('p', class_='content__list--item--title')
        title = p_title.find('a').string.split(' ')[10].replace('▪', '·').replace('•', '·').replace('\u200b', '') \
            .replace('\u2022', '·')
        p_des = content_main.find('p', class_='content__list--item--des')
        des = p_des.find_all('a')
        try:
            restrict = des[0].string
        except:
            restrict = ''
        des_str = ''
        for d in des:
            if d.string is None:
                continue
            de = d.string.replace('▪', '·').replace('•', '·').replace('\u200b', '').replace('\u2022', '')
            des_str = des_str + de
        p_brand = content_main.find('p', class_='content__list--item--brand')
        try:
            brand = p_brand.find('span', class_='brand').string.strip()
        except:
            brand = ''
        des_str = des_str.replace('\u200b', '').replace('\u2022', '')
        info3 = [title, restrict, des_str, brand]
        info3_total = info3_total + [info3]
    return detail_url, info3_total


def get_price(soup):
    div_list1 = soup.find_all('div', class_='content__aside--title')
    unit = str(div_list1[0].contents[2]).replace(' ', '').replace('\n', '')  # 单位
    price = ''
    for div in div_list1:
        price = str(div.find('span'))
        price = price.replace('<span>', '')
        price = price.replace('</span>', unit)
        # print(price)
    return price


def get_info1(soup):
    div_list1 = soup.find('div', class_='content__subtitle')
    time = div_list1.contents[0].replace('房源维护时间：', '').strip()
    div_list2 = soup.find_all('div', class_='content__aside')
    info1 = []
    for div in div_list2:
        info_list = div.find('ul')
        info = info_list.find_all('li')
        ss_strs = []
        for ss in info:
            ss_str = str(ss).replace('<li>', '').replace('<span class="label">', '').replace('</span>', ' ').replace(
                '</li>', ' ').replace('\n', '').replace('\u200b', '').replace('\u2022', '').split(' ')
            ss_strs = ss_strs + [ss_str]
        rent = ss_strs[0][1]
        house_type = ss_strs[1][1]
        cover = ss_strs[1][2]
        finish = ss_strs[1][3]
        info1 = [time, rent, house_type, cover]
    return info1


def get_info2(soup):
    div_list = soup.find_all('div', class_='content__article__info')
    info2 = []
    for div in div_list:
        ul_list = div.find_all('ul')
        item_info = []
        for ul in ul_list:
            info = ul.find_all('li')
            for item in info:
                item_str = str(item).replace('<li class="fl oneline">', '').replace('</li>', '')
                item_info = item_info + [item_str]
        orientation = item_info[2].replace('朝向：', '')
        term = item_info[18].replace('租期：', '')
        floor = item_info[7].replace('楼层：', '')
        elevator = item_info[8].replace('电梯：', '')
        info2 = [orientation, term, floor, elevator]
    return info2


def get_end_page(soup):
    content = soup.find('div', class_='content')
    content_pg = content.find('div', class_='content__pg')
    end_pg = int(content_pg.get('data-totalpage'))
    return int(end_pg)


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}
# 待搜索的url
base_urls = ["https://sz.lianjia.com/zufang/longhuaqu/"]
# 对应的城市
# cities = ['苏州', '苏州', '苏州', '苏州', '苏州', '苏州', '苏州', '苏州', '苏州', '苏州']
cities = ['深圳', '深圳', '深圳', '深圳', '深圳', '深圳', '深圳', '深圳', '深圳', '深圳']
txt_content = []
output_dir = 'C:/Users/Dai Lingyun/Desktop/rent/'
# 区域 方式 租金 户型 朝向 品牌 租期 楼层 电梯
# address location rent price house_type orientation brand term floor elevator

for base_url, city in zip(base_urls, cities):
    # get_urls(base_url, 起始页数,终止页数)
    print(base_url)
    response0 = requests.get(url=base_url, headers=headers).text
    soup0 = BeautifulSoup(response0, "lxml")
    end_pg = get_end_page(soup0) + 1
    urls = get_urls(base_url, 65, end_pg)
    with open(output_dir + city + '.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["标题", "地区", "地址", "品牌", "月租", "房源维护时间", "租房类型", "房型", "面积", "朝向", "租期", "楼层", "电梯"])
        count = 64
        for url in urls:
            house_urls, info3_total = get_detail_url(url, headers)
            count1 = 1
            response1 = requests.get(url=url, headers=headers).text
            soup1 = BeautifulSoup(response1, "lxml")
            content = soup1.find('div', class_='content')
            content_article = content.find('div', class_='content__article')
            content_empty = content_article.find('div', class_='content__empty1')
            if content_empty is not None:
                print(content_empty)
                continue
            for house, info3 in zip(house_urls, info3_total):
                response = requests.get(url=house, headers=headers).text
                soup = BeautifulSoup(response, "lxml")
                try:
                    price = get_price(soup)
                except:
                    # print("price error")
                    continue
                    # print("price error")
                try:
                    info1 = get_info1(soup)
                except:
                    # print("info1 error")
                    continue
                    # print("info1 error")
                try:
                    info2 = get_info2(soup)
                except:
                    # print("info2 error")
                    continue
                    # print("info2 error")
                info = info3 + [price] + info1 + info2
                # print(info)
                try:
                    writer.writerow(info)
                except:
                    print(info)
                    writer.writerow(info)
                # except:
                # continue
                print('count1:', count1)
                count1 = count1 + 1
            # writer.writerow('')
            count = count + 1
            print(count)
