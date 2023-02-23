# -*- coding: UTF-8 -*-
#!/usr/bin/python3

"""
半自动化的亚马逊asin爬虫，用于手动补爬虫数据用。
@Author ：Patrick Lam
@Date ：2023-02-23
"""

from playwright.sync_api import Playwright, sync_playwright, expect
import time
from lxml import etree
import datetime
import re
import pandas as pd
import os

main_url = 'https://www.amazon.ca/dp/'
asin_list = []
# 从txt中读取目标asin
with open('config/CA.txt', 'r') as f:
    arr = f.readlines()
    for asin in arr:
        a = asin.strip()
        asin_list.append(a)
print('读取目标txt完毕，一共有{}个asin'.format(str(len(asin_list))))

df_result = pd.DataFrame(columns=('product_url', 'title', 'reviews', 'stars',
                                  'rank1', 'cat1', 'rank2', 'cat2', 'first_available_date',
                                  'qna', 'first_img', 'price_type', 'price', 'total_cat',
                                  'spider_time', 'station', 'brand', 'is_fba',
                                  'description', 'coupon'))


def run(playwright: Playwright) -> None:
    total_cnt = len(asin_list)
    i = 0
    for asin in asin_list:
        i += 1
        url = main_url + asin
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        # if ''
        context.set_default_timeout(800000)
        page = context.new_page()
        retry_cnt = 0
        text = ''
        while retry_cnt <= 3:
            page.goto(url, wait_until="domcontentloaded")
            page.reload()
            page.keyboard.press("End")
            # 暂停1秒等待页面加载
            time.sleep(1)
            text = page.content()
            if 'Enter the characters you see below' in text:
                print('遇到验证码，等到人工输入验证码')
                page.pause()
                continue
            else:
                break
        html = etree.HTML(text)
        title = html.xpath('//span[@id="productTitle"]/text()')
        print(title)
        spider_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        brand_info = html.xpath('//a[@id="bylineInfo"]/text()')
        if 'Store' in ''.join(brand_info):
            brand = re.findall(r'Visit the (.*) Store', ''.join(brand_info))[0]
        elif 'Brand' in ''.join(brand_info):
            brand = ''.join(brand_info).split('Brand', 1)[1].replace(':', '').strip()
        else:
            brand = 'none'
        merchant_infos = html.xpath('//div[@id="merchant-info"]//text()')
        is_fba = 'none'
        if merchant_infos:
            for merchant_info in merchant_infos:
                if 'sold by Amazon' in ''.join(merchant_info):
                    is_fba = '自营'
                    break
                elif 'Fulfilled by Amazon' in ''.join(merchant_info):
                    is_fba = 'FBA'
                    break
            else:
                is_fba = '第三方'
        print(is_fba)
        reviews = html.xpath(
            '//div[@id="averageCustomerReviews"]'
            '//a[@id="acrCustomerReviewLink"]/span[@id="acrCustomerReviewText"]/text()')
        reviews = ''.join(reviews).split(' ', 1)[0].replace(',', '')
        print('rv: ' + reviews)
        stars = html.xpath(
            '//div[@id="averageCustomerReviews"]//span[@id="acrPopover"]/span/a/i/span/text()')
        stars = ''.join(stars).strip().split(' ', 1)[0]
        print('stars: ' + stars)

        if 'a-section table-padding' in text:
            # 排名1，样例：#3,238 in Home & Kitchen，以空格分割，取第一个元素并去除#和逗号
            rank1 = html.xpath(
                '//*[@id="productDetails_detailBullets_sections1"]/tr/td/span/span[1]/text()[1]')
            rank1 = ''.join(rank1).split(' ', 1)[0].replace('#', '').replace(',', '')
            # 类目1，样例：See Top 100 in Home & Kitchen，取单词in后面的字符串
            cat_1 = html.xpath(
                '//*[@id="productDetails_detailBullets_sections1"]/tr/td/span/span[1]/a/text()')
            if 'in' in ''.join(cat_1):
                cat_1 = ''.join(cat_1).split('in')[1]
            else:
                cat_1 = ''.join(cat_1)
            # 排名2，样例：#23
            rank2 = html.xpath(
                '//*[@id="productDetails_detailBullets_sections1"]/tr/td/span/span[2]/text()')
            rank2 = ''.join(rank2).split(' ', 1)[0].replace('#', '').replace(',', '')
            # 类目2，样例：Bed Throws
            cat_2 = html.xpath(
                '//*[@id="productDetails_detailBullets_sections1"]/tr/td/span/span[2]/a/text()')
            cat_2 = ''.join(cat_2)
            # 首次上架日期
            first_available_date = html.xpath(
                '//th[contains(text(),"Date First Available")]/following-sibling::td/text()')
            first_available_date = ''.join(first_available_date)
        else:
            rank1 = html.xpath(
                '//div[@id="detailBulletsWrapper_feature_div"]/ul[1]/li/span//text()[2]')
            rank1 = ''.join(rank1).strip().split(' ', 1)[0].replace('#', '').replace(',', '')
            cat_1 = html.xpath(
                '//div[@id="detailBulletsWrapper_feature_div"]/ul[1]/li/span/a/text()')
            if 'in' in ''.join(cat_1):
                cat1 = ''.join(cat_1).split('in')[1]
            else:
                cat1 = ''.join(cat_1)
            rank2 = html.xpath(
                '//div[@id="detailBulletsWrapper_feature_div"]/ul/li/span/ul/li/span/text()'
            )
            rank2 = ''.join(rank2).strip().split(' ', 1)[0].replace('#', '').replace(',', '')
            cat_2 = html.xpath(
                '//div[@id="detailBulletsWrapper_feature_div"]/ul/li/span/ul/li/span/a/text()')
            cat_2 = ''.join(cat_2)
            first_available_date = html.xpath(
                '//span[contains(text(),"Date First Available")]/following-sibling::span/text()')

            first_available_date = ''.join(first_available_date)
        print(str(rank1) + ' ' + str(cat_1) + ' ' + str(rank2) + ' ' + str(cat_2) + '\n' + str(first_available_date))
        # QA问答数
        qna = html.xpath('//*[@id="askATFLink"]/span/text()')
        qna = ''.join(qna).strip().split(' ', 1)[0]
        print('qa: ' + qna)
        # 首图链接
        first_img = html.xpath(
            '//span[@class="a-list-item"]/span[@class="a-declarative"]'
            '/div[@id="imgTagWrapperId"]/img/@src')
        first_img = ''.join(first_img)
        # 价格标签，区分ourprice和dealprice
        price_tag = html.xpath('//table[contains(@class,"a-lineitem a-align-top")]/'
                               'tr/td[@class="a-span12"]/span[1]/@id')
        price_type = ''
        if 'ourprice' in ''.join(price_tag):
            price_type = 'ourprice'
        elif 'saleprice' in ''.join(price_tag):
            price_type = 'saleprice'
        elif 'dealprice' in ''.join(price_tag):
            price_type = 'dealprice'
        print(price_type)
        # 价格
        price = html.xpath(
            '//*[@id="corePrice_desktop"][1]/div/table/tr/td[2]/span[@class="a-price a-text-price a-size-medium apexPriceToPay"]/span[1]/text()')
        price2 = html.xpath(
            '//*[@id="corePriceDisplay_desktop_feature_div"]/div[@class="a-section a-spacing-none aok-align-center"]//span[@class="a-offscreen"]/text()')
        if price:
            prc = price[0].strip()
        elif price2:
            prc = price2[0].strip()
        else:
            prc = price2[0]
        print('price: ' + prc)
        # 完整类目
        cats1 = html.xpath(
            '//ul[@class="a-unordered-list a-horizontal a-size-small"]/li/span//text()')
        # cats2 = [''.join(i) for i in cats1]
        cats2 = []
        for cat1 in cats1:
            if len(cat1) > 0:
                cats2.append(cat1.strip())
                cats2.append(' ')
        total_cat = ''.join(cats2)
        print('total_cat: ' + total_cat)
        # 产品卖点
        descriptions = html.xpath('//div[@id="feature-bullets"]/ul//li[not(@id)]/span//text()')
        description = ''
        # print(descriptions)
        for desc in descriptions:
            description = description + '\n' + str(desc).strip()
        description = description.strip()
        # coupon数据
        coupon = html.xpath('//*[contains(@id,"couponText")]/text()')
        coupon = ''.join(coupon).strip()
        print('coupon: ' + coupon)
        temp_dict = {
            'product_url': url,
            'title': ''.join(title).strip(),
            'reviews': reviews,
            'stars': stars,
            'rank1': rank1,
            'cat1': ''.join(cat_1),
            'rank2': rank2,
            'cat2': ''.join(cat_2),
            'first_available_date': first_available_date,
            'qna': qna,
            'first_img': first_img,
            'price_type': price_type,
            'price': prc,
            'total_cat': total_cat,
            'spider_time': spider_time,
            'station': 'CA',
            'brand': brand,
            'is_fba': is_fba,
            'description': description,
            'coupon': coupon
        }
        df_result.loc[len(df_result)] = temp_dict
        print('完成第{}个asin爬取，还有{}个目标asin'.format(str(i), str(total_cnt-i)))
        page.close()
        context.close()
        browser.close()
        time.sleep(0.9)


with sync_playwright() as playwright:
    run(playwright)
    file_name = 'amazon关键词爬取结果0223.csv'
    file_path = os.path.join(os.getcwd(), file_name)
    df_result.to_csv(file_path, index=False, sep=',', encoding='utf-8-sig')

