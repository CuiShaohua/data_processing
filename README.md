# 

## 1 百度学术科技论文爬虫（为读博的朋友写的）
### 1、 运行方法  
```python
python literatur_spyder.py
```

## 2 爬取某个教授的百度学术主页，并对发表过的文章信息进行汇总
使用步骤：
### 1、安装selenium，模拟浏览器点击下一页  
```Python
pip install selenium
```  
### 2、下载chromedriver(注意对应自己的chrome版本即可，亲测win32可以用到64位OS上)  
```
http://npm.taobao.org/mirrors/chromedriver/
```  
### 3、更改url为你想爬取的教授百度学术主页。
![iamge]()

### 4、 Have Hack ~
```python
python professor.py
```


QA:
(1)为什么不采用1的方法自己写，而是采用selenium？  
```因为python自己写的针对于教授的论文，存在url不变翻页的情况，并且，_token的计算采用了md5（time_stamp + token + 某个字符串）的方式，但是token的获取应该是百度数据库中直接生成的，爬不到。所以采用selenium的方式可以直接模拟浏览器翻页```  
(2)采用selenium进行爬虫有没有坏处？  
```首先得承认是有的，selenium可能等不到网页的内容全部加载就开始爬取，这个问题也有人针对不同的开发情况去解决，但是在本文的这种情况下，抓取一页20个论文标签，没有实现，只能是加大sleep时间去做，因此不能保证爬取全面。大概850篇文章能爬取780多左右。```  



