#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests, os, re, random, time
from urllib.parse import urlencode
from urllib import parse
from bs4 import BeautifulSoup
import pandas as pd

def get_page(keywords, offset, search_mode=1):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
    }
    # 传递给浏览器的参数

    params = {
        'wd': keywords,  #
        'pn': offset,  # offset 第几页
        'tn': 'SE_baiduxueshu_c1gjeupa',  #
        'ie': 'utf-8',  # 编码
        'sc_hit': '1'  #
    }

    url = "http://xueshu.baidu.com/s?" + urlencode(params)
    citatation_url = url + "&sort=sc_cited"

    try:
        if search_mode == 1:
            response = requests.get(url, headers=headers)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
        elif search_mode == 2:
            response = requests.get(citatation_url, headers=headers)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
    except requests.ConnectionError:

        return None

# 对于每页的文献信息（每页基本包含10篇文献），提取所有的文献主题、作者、摘要、文献详细地址
def get_urls(text):

    all_titles = []  # 主题   existed
    all_authors = []  # 作者   existed
    all_paper_urls = []  # 论文初步网址  existed

    soup = BeautifulSoup(text, 'lxml')
    title_datas = soup.select('div.sc_content > h3 > a')  # select返回值类型为<class 'list'>
    #print(title_datas)

    author_datas = soup.find_all('div', 'sc_info')  # find_all返回值类型为<class 'bs4.element.ResultSet'>
    for item in title_datas:
        result = {
            'title': item.get_text(),
            'href': item.get('href')  # 关于论文的详细网址，经过观察发现需要提取部分内容
            # http://xueshu.baidu.com/usercenter/paper/show?paperid=389ef371e5dae36e3a05b187f7eb2a95&site=xueshu_se
            # /s?wd=paperuri%3A%28389ef371e5dae36e3a05b187f7eb2a95%29&filter=sc_long_sign&sc_ks_para=q%3D%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0%E7%A0%94%E7%A9%B6%E7%BB%BC%E8%BF%B0&sc_us=11073893925633194305&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8
        }
        # print(result)
        all_titles.append(result["title"])
        # print(str(parse.urlparse(result["href"]).query).split("&")[0])
        wd = str(parse.urlparse(result["href"]).query).split('&')[0]

        paperid = wd.split('=')[1]
        params = {
            'paperid': paperid,
            'site': 'xueshu_se'
        }
        url = 'http://xueshu.baidu.com/usercenter/paper/show?' + urlencode(params)
        all_paper_urls.append(url)

    for authors in author_datas:  # authors类型为<class 'bs4.element.Tag'>
        for span in authors.find_all('span', limit=1):  # 此时span类型为<class 'bs4.element.Tag'>
            each_authors = []
            for alist in span.find_all('a'):
                each_authors.append(alist.string)
            all_authors.append(each_authors)
    return all_titles, all_authors, all_paper_urls

# 用pandas来构造结构，最终输出成表格





def get_download(url):
    #
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
        'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
        'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    ]
    header = random.choice(user_agent_list)
    headers = {
        'User-Agent': header
    }
    try:

        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
    except requests.ConnectionError:
        return None

# 对于每个文献页面爬取的详细页面内容进行提取，找出所有免费下载的地址和可用的信息
def get_download_urls(text, url):

    download_urls = []
    soup = BeautifulSoup(text, 'lxml')
    #print(url)
    try:
        abstract = soup.select("div.c_content > div.abstract_wr > p.abstract")[0].get_text()
    except Exception:
        abstract = "NA"
    #print(abstract)
    # keywords
    keywords = []
    try:
        keywords_list = soup.select("div.kw_wr > p.kw_main > span")
        if keywords_list:
            for item in keywords_list:
                keywords.append(item.get_text())
        else:
            keywords = ["NA"]
    except Exception:
        keywords = ["NA"]
    #print(keywords)

    # 引用次数
    try:
        citation_num_list = soup.select("div.ref_wr > p.ref-wr-num > a")
        if citation_num_list:
            citation_num = citation_num_list[0].get_text().strip()
        else:
            citation_num = "NA"
    except Exception:
        citation_num ="NA"
    #print(citation_num)

    # 文章doi
    try:
        doi_list = soup.select("div.doi_wr > p.kw_main")
        if doi_list:
            DOI = doi_list[0].get_text().strip()
        else:
            DOI = "NA"
    except Exception:
        DOI = "NA"
    #print(DOI)

    # 发表年份
    try:
        publish_year_list = soup.select("div.year_wr > p.kw_main")
        if publish_year_list:
            publish_year = publish_year_list[0].get_text().strip()
        else:
            publish_year = "NA"
    except Exception:
        publish_year = "NA"
    #print(publish_year)

    # 发表期刊
    try:
        publisher_list = soup.select("div > div.container_right > a")
        if publisher_list:
            publisher = ' '.join(re.findall(r'(\d+|\w+)', publisher_list[0].get_text().strip()))
        else:
            publisher = "NA"
    except Exception:
        publisher = "NA"
    #print(publisher)

    # 下载链接（只限一些常见的下载链接）
    pattern = re.compile('<a\sclass="dl_item".*?href="(.*?)".*?<span\sclass="dl_source".*?>(.*?)</span>', re.S)
    try:
        results = re.findall(pattern, text)
        # 加一判断, result匹配到了结果
        if len(results) != 0:
            for item in results:
                # 下载链接做一个排序：根据下载速度经验，Elsiver>Springer>"知网">其他
                if item[1] in ['Elsevier','Springer','知网','ResearchGate','Wiley', 'EBSCO','Cambridge University','dx.doi.org']:
                    download_urls.append({item[1]: item[0]})
        elif len(results) == 0: # 没有匹配到则返回原网址
            download_urls.append({"请去原网站查看!":url})

    except Exception as e:
        print(e)
    #print(download_urls)
    return  abstract, keywords, citation_num, DOI, publish_year, publisher,download_urls

# 写入excel


if __name__ == '__main__':

    # -------- 程序入口处 ------------------
    print
    u"""#---------------------------------------
    #   程序：百度学术关键词检索下载文献基本信息（包含常见的下载地址）
    #   版本：1.1
    #   作者：Appra
    #   日期：2020-01-08  Miss
    #   语言：Python 3.6
    #   操作：输入关键词后爬取所有相关文献信息，将文献基本信息，爬取下来并保存到xslx文件
    #   功能：将查询的文献信息免费下载地址打包txt存储到本地。
    #---------------------------------------
    """

    # keywords = "Ti6Al4V"
    search_words = str(input("请输入在百度学术网站需要查询的关键词：\n"))
    print("开始爬取百度学术网站关于“{}”关键词的相关内容".format(search_words))
    choice = input("搜索结果按相关性排列按1 or 按被引量排列按2:\n")
    print(choice)
    try:
        if choice == '1':  # 按相关性搜索结果
            dfs = pd.DataFrame()
            for i in range(10):
                print("开始爬取第{}页的内容".format(str(i + 1)))
                offset = i * 10
                text = get_page(search_words, offset)
                all_titles, all_authors, all_paper_urls = get_urls(text)  # 还有几个标题
                #print(len(all_paper_urls))
                all_abstracts = []  # 摘要  existed
                all_keywords = []  # 关键词 existed
                all_paper_doi = []  # 文章doi号 existed
                all_paper_citation = []  # 被引量  may be existed
                all_paper_publish_time = []  # 发表年限
                all_paper_publisher = []  # 出版商
                all_dlUrls = []  # 下载链接
                for k in range(len(all_paper_urls)):
                    #print(k)
                    new_text = get_download(all_paper_urls[k])

                    abstract, keywords, citation_num, DOI, publish_year, publisher,download_urls = get_download_urls(new_text, all_paper_urls[k])
                    all_dlUrls.append(download_urls)
                    all_abstracts.append(abstract)
                    all_keywords.append(keywords)
                    all_paper_doi.append(DOI)
                    all_paper_citation.append(citation_num)
                    all_paper_publish_time.append(publish_year)
                    all_paper_publisher.append(publisher)

                # 建立字典
                Paper_info = {
                    "Title":all_titles,
                    "Authors":all_authors,
                    "Keywords":all_keywords,
                    "Abstract":all_abstracts,
                    "Publisher": all_paper_publisher,
                    "PublisherTime":all_paper_publish_time,
                    "BaiduXueShuLink": all_paper_urls,
                    "PaperDOI":all_paper_doi,
                    "CitationNum": all_paper_citation,
                    "AvailDownloadLinks": all_dlUrls,

                }
                #print(len(Paper_info))
                #df = pd.DataFrame(Paper_info)

                df = pd.DataFrame.from_dict(Paper_info)
                dfs = dfs.append(df, ignore_index=True)
                #print(dfs)
            writer = pd.ExcelWriter(search_words +'sortedByRealation.xlsx')
            dfs.to_excel(writer, sheet_name='Data1', startcol=0, index=True)
            writer.save()
            print("保存成功！")

        elif choice == "2":  # 按被引用次数搜索
            dfs = pd.DataFrame()
            for i in range(10):
                print("开始爬取第{}页的内容".format(str(i + 1)))
                offset = i * 10
                text = get_page(search_words, offset, search_mode=2)
                all_titles, all_authors, all_paper_urls = get_urls(text)  # 还有几个标题
                all_abstracts = []  # 摘要  existed
                all_keywords = []  # 关键词 existed
                all_paper_doi = []  # 文章doi号 existed
                all_paper_citation = []  # 被引量  may be existed
                all_paper_publish_time = []  # 发表年限
                all_paper_publisher = []  # 出版商
                all_dlUrls = []  # 下载链接
                for k in range(len(all_paper_urls)):
                    new_text = get_download(all_paper_urls[k])
                    abstract, keywords, citation_num, DOI, publish_year, publisher,download_urls = get_download_urls(new_text, all_paper_urls[k])
                    all_dlUrls.append(download_urls)
                    all_abstracts.append(abstract)
                    all_keywords.append(keywords)
                    all_paper_doi.append(DOI)
                    all_paper_citation.append(citation_num)
                    all_paper_publish_time.append(publish_year)
                    all_paper_publisher.append(publisher)
                    #print(all_paper_publisher)

                # 建立字典
                Paper_info = {
                    "Title":all_titles,
                    "Authors":all_authors,
                    "Keywords":all_keywords,
                    "Abstract":all_abstracts,
                    "Publisher": all_paper_publisher,
                    "PublisherTime":all_paper_publish_time,
                    "BaiduXueShuLink": all_paper_urls,
                    "PaperDOI":all_paper_doi,
                    "CitationNum": all_paper_citation,
                    "AvailDownloadLinks": all_dlUrls,

                }
                print(len(Paper_info))
                #df = pd.DataFrame(Paper_info)

                df = pd.DataFrame.from_dict(Paper_info)
                dfs = dfs.append(df, ignore_index=True)
                #print(dfs)
            writer = pd.ExcelWriter(search_words +'sortedByDownloadNum.xlsx')
            dfs.to_excel(writer, sheet_name='Data1', startcol=0, index=True)
            writer.save()
            print("保存成功！")
    except Exception as e:
        print(e)

