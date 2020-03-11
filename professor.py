from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, re, random, requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  # available since 2.26.0


def HomePageInfo(browser):  # 首页信息爬取
    title = browser.find_elements_by_xpath('//*[@id="articlelist_container"]/div[2]/div[1]')
    content = title[0].get_attribute('innerHTML')
    soup = BeautifulSoup(content, 'lxml')
    title_datas = soup.select('div.res_con > h3 > a')  # select返回值类型为<class 'list'>
    all_titles = []
    all_paper_urls = []

    #print(len(title_datas))
    for item in title_datas:
        result = {
            'title': item.get_text(),
            'href': item.get('href')  # 关于论文的详细网址，经过观察发现需要提取部分内容
        }
        # print("title_data result is {}".format(result))
        all_titles.append(result["title"])
        # print("titles are {}".format(all_titles))
        url = 'http:' + result["href"]
        all_paper_urls.append(url)

    #print(len(all_paper_urls))
    try:
        # publish year
        author_datas = soup.select('div.res_info > span.res_year')  # find_all返回值类型为<class 'bs4.element.ResultSet'>
        publish_years = []
        for span in author_datas:
            publish_years.append(span.get_text())

    except Exception as e:
        print(e)

    return all_titles, all_paper_urls


# 页面的详细内容爬取
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
        #print(abstract)
    except Exception:
        abstract = None
    #print(abstract)
    # keywords
    keywords = []
    try:
        keywords_list = soup.select("div.kw_wr > p.kw_main > span")
        if keywords_list:
            for item in keywords_list:
                keywords.append(item.get_text())
        else:
            keywords = None
    except Exception:
        keywords = None
    #print(keywords)

    # author
    #Author1, Author2, Author3 = None, None, None
    Author = []
    try:
        authors = soup.select("#dtl_l > div.main-info > div.c_content > div.author_wr > p.author_text > span> a")
        for author in authors:
            Author.append(author.get_text().strip())
    except Exception:
        Author.append(None)
    print(Author)
    names = locals()
    # 一定要凑足3个
    if len(Author) == 0:
        Author1 = None
        Author2 = None
        Author3 = None
    elif len(Author) == 1:
        Author1 = Author[0]
        Author2 = None
        Author3 = None
    elif len(Author) == 2:
        Author1 = Author[0]
        Author2 = Author[1]
        Author3 = None
    elif len(Author) >= 3:
        Author1, Author2, Author3 = Author[0], Author[1], Author[2]

    print(Author1, Author2, Author3)
    # 引用次数
    try:
        citation_num_list = soup.select("div.ref_wr > p.ref-wr-num > a")
        if citation_num_list:
            citation_num = citation_num_list[0].get_text().strip()
        else:
            citation_num = None
    except Exception:
        citation_num =None
    #print(citation_num)

    # 文章doi
    try:
        doi_list = soup.select("div.doi_wr > p.kw_main")
        if doi_list:
            DOI = doi_list[0].get_text().strip()
        else:
            DOI = None
    except Exception:
        DOI = None
    #print(DOI)

    # 发表年份
    try:
        publish_year_list = soup.select("div.year_wr > p.kw_main")
        if publish_year_list:
            publish_year = publish_year_list[0].get_text().strip()
        else:
            publish_year = None
    except Exception:
        publish_year = None
    #print(publish_year)

    # 发表期刊
    try:
        publisher_list = soup.select("div > div.container_right > a")
        if publisher_list:
            publisher = ' '.join(re.findall(r'(\d+|\w+)', publisher_list[0].get_text().strip()))
        else:
            publisher = None
    except Exception:
        publisher = None
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
    return  abstract, Author1, Author2, Author3, keywords, citation_num, DOI, publish_year, publisher,download_urls



'''
    for authors in author_datas:  # authors类型为<class 'bs4.element.Tag'>
        for span in authors.find_all('span'):  # 此时span类型为<class 'bs4.element.Tag'>
            publish_year = []
            try:
                print(span.find_all('a').get_text())
            except Exception:
                pass

            for alist in span.find_all('a'):
                each_authors.append(alist.string)
            all_authors.append(each_authors)           
'''



if __name__ == "__main__":
    # 某个老师的百度学术主页
    url = "http://xueshu.baidu.com/scholarID/CN-B8748R1J"

    chrome_options = Options()
    # specify headless mode
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)
    browser.set_page_load_timeout(600)
    browser.set_script_timeout(600)
    browser.get(url)

    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="articlelist_container"]/div[2]/div[1]/div[20]')))  # index="19"
    #browser.implicitly_wait(10)

    title = browser.find_elements_by_xpath('//*[@id="articlelist_container"]/div[2]/div[1]')
    content = title[0].get_attribute('innerHTML')
    soup = BeautifulSoup(content, 'lxml')

    Title, ArticleUrl = HomePageInfo(browser)

    # 开始第二页以后的内容
    PageNumInfo = browser.find_elements_by_xpath('//*[@id="articlelist_container"]/div[2]/div[2]/p/span[7]')  # 有隐患
    try:
        PageNum = int(PageNumInfo[0].get_attribute('innerHTML'))
    except Exception as e:
        print(e)
    for i in range(1, PageNum):
        # 点击下一页
        nextPage = browser.find_element_by_xpath('//*[@id="articlelist_container"]/div[2]/div[2]/p/a[2]/i')
        #print(nextPage.text)
        nextPage.click()
        time.sleep(2)
        browser.set_page_load_timeout(800)
        browser.set_script_timeout(800)

        # 爬取第i页数据
        each_page_title, each_article_url = HomePageInfo(browser)
        Title += each_page_title
        ArticleUrl += each_article_url

    ### 爬完连接再下载吧
    Abstract, Author1,Author2,Author3, Keywords, CitationNum, DOIS, PublishYear, Publisher, DownloadUrls = [], [],[], [], [], [], [],[],[], []

    for URL in ArticleUrl:

        try:
            text = get_download(URL)
            #print(text)
            if text:
                abstract, author1,author2,author3, keywords, citation_num, DOI, publish_year, publisher,download_urls = get_download_urls(text, url)  #
                Abstract.append(abstract)
                Author1.append(author1)
                Author2.append(author2)
                Author3.append(author3)
                Keywords.append(keywords)
                CitationNum.append(citation_num)
                DOIS.append(DOI)
                PublishYear.append(publish_year)
                Publisher.append(publisher)
                DownloadUrls.append(download_urls)
        except Exception as e:
            print(e)
    Paper_info = {
        "Title": Title,
        "Author1": Author1,
        "Author2": Author2,
        "Author3": Author3,
        "Keyword": Keywords,
        "Abstract": Abstract,
        "Publisher": Publisher,
        "PublisherTime": PublishYear,
        "BaiduXueShuLink": ArticleUrl,
        "PaperDOI": DOIS,
        "CitationNum": CitationNum,
        "AvailDownloadLinks": DownloadUrls,

    }

    df = pd.DataFrame.from_dict(Paper_info)
    df.transpose()
    try:
        writer = pd.ExcelWriter('LiJinshan.xlsx')
        df.to_excel(writer, sheet_name='Data1', startcol=0, index=True)
        writer.save()
    except Exception as e:
        print(e)
    browser.quit()
