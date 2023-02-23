# 前言
本项目是一个半自动的亚马逊asin爬虫，在遇到验证码时，可通过人工输入验证码的方式确保爬虫正常爬取。当前代码实现的是亚马逊CA站点。
# 项目环境
python环境需要3.7.5以上

结果数据保存到csv
# 项目启动
1、修改爬取的asin目标，请修改config/CA.txt

2、修改爬取的站点，请修改`amazon_crawl_playwright.py`中的`main_url`

3、需要录入到mysql，请运行`save_csv.py`

4、程序本体直接运行`amazon_crawl_playwright.py`