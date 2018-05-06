# -*- coding:utf-8 -*-  
"""
--------------------------------
    @Author: Dyson
    @Contact: Weaver1990@163.com
    @file: TuPaiWang.py
    @time: 18-4-27 下午3:15
--------------------------------
"""
import sys
import os
import imp
import requests
import bs4
import pandas as pd
import re
import time

sys.path.append("/home/dyson/Documents/MyWheels3")
imp.reload(sys)
#sys.setdefaultencoding('utf8')
#import set_log  # log_obj.debug(文本)  "\x1B[1;32;41m (文本)\x1B[0m"

#log_obj = set_log.Logger('TuPaiWang.log', set_log.logging.WARNING,
#                         set_log.logging.DEBUG)
#log_obj.cleanup('TuPaiWang.log', if_cleanup=True)  # 是否需要在每次运行程序前清空Log文件

headers = {'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
            'Connection': 'keep-alive'
            }

scan_page = 102
class TuPaiWang(object):

    def __init__(self):
        pass

    def main(self):
        url0 = "http://tdjy.zjdlr.gov.cn/GTJY_ZJ/noticelist_page?SSXZQ=&RESOURCELB=" \
              "&GDLB=&JYFS=&NOTICENO=&NOTICENAME=&checkNOTICENAME=&startDate=&endDate=" \
              "&zylb=01&currentPage="

        # df = pd.DataFrame([])
        for release_time, announcement_url in self.catelog_parse(url0):
            time.sleep(1)
            for detail_url in self.announcement_parse(announcement_url):
                time.sleep(1)
                for ser0, file_url in self.detail_parse(detail_url):
                    time.sleep(1)
                    ser = ser0.append(pd.Series({"发布时间":release_time}))
                    # print(ser)

                    # df = df.append(ser, ignore_index=True)
                    # df.to_excel("/home/dyson/Desktop/data.xlsx")
                    self.file_parse(file_url, "%s_%s" %(ser["所属行政区"], ser["地块编号"].replace('/','')))

    def catelog_parse(self, url0):
        global scan_page

        for i in range(81, scan_page+1):
            url = url0 + str(i+1)
            print("目录页：" + url)

            global headers
            resp = requests.get(url, headers=headers)
            bs_obj = bs4.BeautifulSoup(resp.content, 'html.parser')
            e_table = bs_obj.table

            for e_a in e_table.find_all('a'):
                s = e_a.get('onclick')
                s_list = re.findall("(?<=')\d+?(?=')", s)

                release_time = e_a.parent.find_previous_sibling('td').get_text(strip=True)
                new_url = "http://tdjy.zjdlr.gov.cn/GTJY_ZJ/noticeDetailAction?NOTICEID={0}&GDLB={1}".format(*s_list)

                yield release_time, new_url

    def announcement_parse(self, announcement_url):
        print("公告页：" + announcement_url)

        global headers
        resp = requests.get(announcement_url, headers=headers)
        bs_obj = bs4.BeautifulSoup(resp.content, 'html.parser')
        e_table = bs_obj.table

        for e_a in e_table.find_all('a'):
            s = e_a.get('href')
            s_list = re.findall("(?<=')\d+?(?=')", s)

            new_url = "http://tdjy.zjdlr.gov.cn/GTJY_ZJ/landinfo?ResourceID={0}&flag={1}".format(*s_list)

            yield new_url

    def detail_parse(self, detail_url):
        print("详情页：" + detail_url)

        global headers
        resp = requests.get(detail_url, headers=headers)
        bs_obj = bs4.BeautifulSoup(resp.content, 'html.parser')

        file_div = bs_obj.find('div', class_='bt')
        file_id = re.search("(?<=javascript:downLoadDoc\(')\d+?(?='\))", file_div.prettify()).group()
        file_url = "http://tdjy.zjdlr.gov.cn/GTJY_ZJ/downFileAction?rid=%s&fileType=1" %file_id

        e_div = bs_obj.find('div', class_='cotain-box')
        e_table1 = e_div.find('td', class_='font_btn').table
        df1 = pd.read_html(e_table1.prettify(), header=0)[0]

        ser = df1.iloc[0].dropna()

        e_table2 = e_div.find('td', class_='td_line2').table
        df2 = pd.read_html(e_table2.prettify())[0]
        df21 = df2[[0, 1]].dropna(axis=0).set_index([0, ]).T
        df22 = df2[[2, 3]].dropna(axis=0).set_index([2, ]).T

        ser = ser.append(df21.iloc[0]).append(df22.iloc[0])

        yield ser, file_url

    def file_parse(self, file_url, dir_name):
        print("文件下载页：" + file_url)

        global headers
        resp = requests.get(file_url, headers=headers)
        bs_obj = bs4.BeautifulSoup(resp.content, 'html.parser')

        for e_a in bs_obj.find_all('a'):
            s = e_a.get('onclick')
            s_list = re.findall("(?<=')[^,]+?(?=')", s)

            new_url = "http://tdjy.zjdlr.gov.cn/GTJY_ZJ/download?RECORDID={0}&fileName={1}".format(*s_list)
            print("正在下载文件：" + new_url)

            path = "/home/dyson/Desktop/files/%s/" %dir_name
            path = re.sub("[()（）\s]", '', path)[:80]
            if not os.path.exists(path):
                os.system("mkdir %s" %path)

            self.get_file(new_url, path + s_list[-1])
        # http://tdjy.zjdlr.gov.cn/GTJY_ZJ/download?RECORDID=24986&fileName=%CE%A2%D0%C5%CD%BC%C6%AC_20180426114625.jpg

    def get_file(self, url, targetfile):
        global headers
        r = requests.get(url, headers=headers)
        with open(targetfile, "wb") as code:
            code.write(r.content)
            print("====>>>Successfully saving %s" %targetfile)

if __name__ == '__main__':
    TuPaiWang = TuPaiWang()
    TuPaiWang.main()
