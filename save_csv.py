# -*- coding: UTF-8 -*-
#!/usr/bin/python3

"""
爬取结果csv批量插入mysql库
@Author ：Patrick Lam
@Date ：2023-02-23
"""

from config.setting import MYSQL_HOST, MYSQL_DBNAME, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT
import pandas as pd
import pymysql


if __name__ == '__main__':
    insert_sql = """
        insert into amazon_craw_asin_details(asin,asin_url,title,reviews,stars,rank1,
                cat1,rank2,cat2,first_available_date,qna,first_img,price_type,price,total_cat,
                spider_time,country,store_name,is_fba,description,coupon) 
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
         """
    conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASSWORD,
                           db=MYSQL_DBNAME, port=MYSQL_PORT, charset='utf8mb4')
    cursor = conn.cursor()
    # 读取csv
    asin_detail = pd.read_csv('config/asin_detail_0201.csv')
    # 批量替换空值，用于mysql插入
    asin_detail.fillna('', inplace=True)
    # 遍历dataframe，通过cursor插入mysql
    for index, row in asin_detail.iterrows():
        cursor.execute(insert_sql, (row['asin'], row['product_url'], row['title'], row['reviews'], row['stars'],
                                    row['rank1'], row['cat1'], row['rank2'], row['cat2'], row['first_available_date'],
                                    row['qna'], row['first_img'], row['price_type'], row['price'], row['total_cat'],
                                    row['spider_time'], row['station'], row['brand'], row['is_fba'],
                                    row['description'], row['coupon'])
                       )
        print("数据已插入：" + str(row['asin']) + ": " + str(row['title']))
        conn.commit()

    cursor.close()
    conn.close()
