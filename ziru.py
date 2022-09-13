import io
import re
from lxml import etree
import pytesseract
from PIL import Image
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/80.0.3987.149 Safari/537.36',
}
base_url = "https://sh.ziroom.com/z/d310118-p"  ###基址：https://sh.ziroom.com/z/z，把z换成p
###改成txt的地址；txt是累计制的，如果要去掉以前的需要先清空这个txt再跑或者新建一个txt
txt_content = []


def get_abstract(url):
    global info_range
    global info_specific
    infomation = []
    ret = requests.get(url=url, headers=headers).text
    with open('ziru.html', 'w', encoding='utf8') as f:
        f.write(ret)
    with open('ziru.html', 'r', encoding='utf8') as f:
        ret = f.read()
    img_url = re.findall('background-image: url\((.*?)\);background-position:', ret)[0]
    px_list = ['0', '21.4', '42.8', '64.2', '85.6', '107', '128.4', '149.8', '171.2', '192.6']
    img_urls = 'https:' + img_url  # 本页面公用的0-9图片
    # img_url='https://static8.ziroom.com/phoenix/pc/images/price/new-list/48d4fa3aa7adf78a1feee05d78f33700.png'
    data = requests.get(url=img_urls, headers=headers).content
    image = Image.open(io.BytesIO(data))
    # vcode是识别出的数字数组
    vcode = pytesseract.image_to_string(image, lang='eng',
                                        config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
    font_dict = {}
    for k, v in enumerate(vcode):
        font_dict[px_list[k]] = v  # font_dict：{'0': '6', ..., '192.6': '3'}
    for i in font_dict:
        ret = ret.replace(
            f'<span class="num" style="background-image: url({img_url});background-position: -{i}px"></span>',
            font_dict[i])
    page_html = etree.HTML(ret)
    div_list = page_html.xpath('/html//section/div[3]/div[2]/div')
    for div in div_list:
        try:
            name = div.xpath('./div[2]/h5/a/text()')[0]
            detail_url = div.xpath('./div[2]/h5/a/@href')[0]
            detail_urls = 'https:' + detail_url  # 详情页网址
            # print(detail_urls)
            try:
                info_range = get_details_2(detail_urls)
                info = info_range
            except:
                info_specific = get_details_1(detail_urls)
                info = info_specific
            # print(info)
            infomation.append(info)

        except:
            continue
        money = ''
        for i in ''.join(div.xpath('./div[2]/div[2]//text()')):
            money += i.strip()
    return infomation


def get_details_range(r):
    page_html = etree.HTML(r)
    div_list = page_html.xpath('/html//section/aside')[0]
    name = div_list.xpath('./*[@class="Z_name"]/text()')[1].replace('\n', '').strip()
    # price = re.findall('<span class="">\d+(?:\.\d+)?\d+(?:\.\d+)?', r)
    price_text_content = div_list.xpath('./div[1]/span[2]//text()')[0].replace('\n', '').strip()
    unit = div_list.xpath('./div[1]/span[3]//text()')[0].replace('\n', '').strip()
    price = price_text_content + unit
    size = div_list.xpath('./div[2]/div[1]/dl[1]/dd[1]//text()')[0]
    orientation = div_list.xpath('./div[2]/div[1]/dl[2]/dd[1]//text()')[0]
    room_type = div_list.xpath('./div[2]/div[1]/dl[3]/dd[1]//text()')[0]
    location = div_list.xpath('./div[2]/ul/li[1]/span[2]//text()')[0]
    floor = div_list.xpath('./div[2]/ul/li[2]/span[2]//text()')[0]
    elevator = div_list.xpath('./div[2]/ul/li[3]/span[2]//text()')[0]
    # heating = div_list.xpath('./div[2]/ul/li[4]/span[2]//text()')[0]
    time_stand = div_list.xpath('/html//section/section/div[4]/div/ul/li[2]/span[2]//text()')[0]
    info = [name, price, size, orientation, room_type, location, floor, elevator, time_stand]
    return info


def get_details_specific(ret):
    img_url = re.findall('background-position:-.*px;background-image: url\((.*?)\);', ret)[-1]
    px_list = ['0', '31.24', '62.48', '93.72', '124.96', '156.2', '187.44', '218.68', '249.92', '281.16']
    img_urls = 'https:' + img_url  # 本页面公用的0-9图片
    data = requests.get(url=img_urls, headers=headers).content
    image = Image.open(io.BytesIO(data))
    vcode = pytesseract.image_to_string(image, lang='eng',
                                        config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
    font_dict = {}
    for k, v in enumerate(vcode):
        font_dict[px_list[k]] = v
    for i in font_dict:
        ret = ret.replace(
            f'<i class="num" style="background-position:-{i}px;background-image: url({img_url});" ></i>',
            font_dict[i])
    for i in font_dict:
        ret = ret.replace(
            f'<i class="num" style="background-position:-{i}px;background-image: url({img_url});"></i>',
            font_dict[i])
    page_html = etree.HTML(ret)
    div_list_ori = page_html.xpath('/html//div/section')[0]
    try:
        name_list = div_list_ori.xpath('./aside/h1')[0]
    except:
        name_list = div_list_ori.xpath('./aside/h3')[0]
    name = name_list.xpath('./text()')[0].replace('\n', '').strip()
    # print(name)
    money = ''
    for i in ''.join(div_list_ori.xpath('./aside/div[1]//text()')):
        money += i.strip()
    div_list = div_list_ori.xpath('./aside/div[@class="Z_home_info"]')[0]
    size = div_list.xpath('./div[1]/dl[1]/dd[1]//text()')[0]
    orientation = div_list.xpath('./div[1]/dl[2]/dd[1]//text()')[0]
    room_type = div_list.xpath('./div[1]/dl[3]/dd[1]//text()')[0]
    location = div_list.xpath('./ul/li[1]/span[2]//text()')[1]
    floor = div_list.xpath('./ul/li[2]/span[2]//text()')[0]
    elevator = div_list.xpath('./ul/li[3]/span[2]//text()')[0]
    # heating = div_list.xpath('./ul/li[4]/span[2]//text()')[0]
    time_list = div_list_ori.xpath('./section/div[@id="rentinfo"]')[0]
    # time_list = div_list_ori.xpath('./section/div[@id="rentinfo"]/div[@id="live_tempbox"]/ul')[0]
    time_stand = time_list.xpath('.//*//ul[@class="jiance"]/li[last()-1]/span[@class="info_value"]/text()')[0]\
        .replace('\t', '').strip()
    info = [name, money, size, orientation, room_type, location, floor, elevator, time_stand]
    return info


def get_details_1(url):
    ret = requests.get(url=url, headers=headers).text
    with open('ziru.html', 'w', encoding='utf8') as f:
        f.write(ret)
    with open('ziru.html', 'r', encoding='utf8') as f:
        ret = f.read()
    info = get_details_specific(ret)
    return info


def get_details_2(url):
    ret = requests.get(url=url, headers=headers).text
    with open('ziru.html', 'w', encoding='utf8') as f:
        f.write(ret)
    with open('ziru.html', 'r', encoding='utf8') as f:
        ret = f.read()
    info = get_details_range(ret)
    return info


with open('E:/learning/code/自如爬虫/ziru_new/ziru/result/house-d310118.txt', 'w', encoding='utf-8') as txt:
    for i in range(1, 51):
        abstract_url = base_url + str(i) + '/'
        print(abstract_url)
        info = get_abstract(abstract_url)
        txt_content.append(info)
        print(info)
        for data in info:
            txt.write(str(data) + '\n')
            txt.flush()
            print(data)

txt.close()
