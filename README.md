# scrapy-news
人民网（People's Daily Online），创办于1997年1月1日，是世界十大报纸之一《人民日报》建设的以新闻为主的大型网上信息交互平台，也是国际互联网上最大的综合性网络媒体之一。本文爬取人民网滚动新闻中经济科技模块，网址如下：http://finance.people.com.cn/GB/70846/index.html

该页面是以新闻列表形式排列，网页末尾有页码，点击不同的页码url中的index序号发生变化。每一条新闻都是以超链接形式存在，点击可以跳转到子页面.
# code
## 思路概述
本文在遵守Robots友好爬虫协议的前提下，在原始新闻列表页面向Web服务器发送携带cookies的请求，提取出子页面超链接，并存储成URL列表。遍历列表，通过selenium模拟浏览器技术，获得每一个子页面的网页内容，而后使用正则表达式、BeautifulSoup库的css选择器，find，findall，select等查找提取元素方法，获取子页面的新闻标题，新闻时间，报道来源，内容，责任编辑，如果页面存在图片或视频元素，提取其超链接后再次发送请求，下载网页内嵌多媒体。
![image](https://github.com/user-attachments/assets/dd5e7518-658f-4e9a-9a4f-918da430406d)
## 1	提取列表新闻链接
因为该网站进行页面翻页需要登录才可完成，所以需要利用cookies的状态保持技术。登录过后利用浏览器抓包工具提取cookie，保存成文本文件方便后续调用。向web服务器发送请求，参数放入url，headers浏览器标识和cookies。由于HTML文本的编码方式是gb2312，所以也选择该编码显示返回的文本文件。

随后利用BeautifulSoup进行文档页面的解析。通过抓包工具可以发现列表主体存放于<div class=”ej_list_box clear”>标签下，因此利用BeautifulSoup库的lxml解析器解析网页文本后，利用find查找元素方法，查找div标签下class 属性值为ej_list_box clear的标签中标签名称为a的，返回查询列表，遍历后提取a标签中的href属性，得到每一条新闻对应的链接，赋给变量href,随后提取a标签下的文本，得到每一条新闻的名字，赋给变量title，因为列表下方有翻页标签，与新闻链接同属一个标签下，但文本显示与新闻不同，所以利用title值做循环的截止，一旦title为数字或者“上一页”时，跳出循环。因为子链接是相对链接，所以将相对链接与基准路径相拼接构造出真实的链接地址，并添加进url列表中。
## 2	提取子页面文本元素
遍历url列表，首先仍然尝试使用requests向web服务器发送请求，得到HTML页面返回结果发现与抓包工具所见不同，查看网页源代码发现该网页是由JavaScript渲染而成，见图表 5 3，所以利用requests不能得到真正的HTML文本。而selenium可以模拟真实的浏览器，返回的HTML文本所见即所得，因此本文利用selenium浏览器模拟技术查看返回后的HTML文本。
- 2.1 提取标题文本

继续利用BeautifulSoup库，选择lxml解析器解析网页文本，利用CSS选择器提取元素。首先提取子页面的标题，利用css选择器的select方法，用.表示class，类名中有空格的，也用.表示，定位出标题所在标签的位置，然后加下标和.text提取出文本，赋值给title。代码如下：
title = bs.select('div.col.col-1.fl > h1')[0].text
- 2.2	提取新闻时间及来源

新闻时间及来源在HTML文件中的位置如下图表 5 7所示：
继续利用上述select方法，将提取出的文本利用split和strip方法去除“|来源”，只保留时间，时间赋给变量date_time,来源赋给变量place，代码如下：
date_time = bs.select('div.col-1-1.fl')[0].text.split("|")[0].strip()
place = bs.select('div.col-1-1.fl > a')[0].text 
- 2.3	提取新闻内容
  
在HTML文件中每个p标签表示一个段落，段落由文本图片或其他多媒体构成。
继续利用上述select方法，利用 > 提取标签下的标签，将提取出的文本列表遍历后利用strip去掉两侧引号，再相加拼接，得到整个页面的完整新闻内容赋值为text
- 2.4	提取责任编辑
  
新闻内容在HTML文件中的位置如下图表 5 11所示，与上述思路一致，提取代码如下：
editor = bs.select('div.edit.cf')[0].text.strip("()")#提取责任编辑

## 3	提取子页面图片链接
利用select定位到img标签后，取出desc属性值作为图片的名字，提取src属性值，即图片的超链接。但是在遍历所有新闻时发现有的文章完全由图构成，每个图没有desc属性，此时截取超链接最后一个/后面的内容作为该图片的名字。接着用文章的标题为名创建文件夹，img_name作为保存后的图片名，向web服务器发送请求，保存返回的二进制文件，也即是下载了图片。

## 4	提取子页面视频链接
因为标签属性较为复杂，所以采用正则表达式提取方法，构造提取的pattern，再预加载正则表达式，解析文本，提取出视频对应的超链接。
## 5	保存元素
新建csv文件，写入标题行，将提取到的标题、时间、内容、来源、责编、新闻网址、图片链接、视频链接写入新建的csv文件中，代码如下所示：

f = open("xinwen.csv", 'w', newline='', encoding='utf-8')
csv.writer(f).writerow(["标题", "时间", "来源", "新闻内容", "责任编辑", "新闻网址", "图片链接", "视频链接"])
csv.writer(f).writerow([title, date_time, place, text, editor, url, img_trueh, video_href])

## 6	设置多线程
为了提高编程效率，本文采用多线程进行爬虫。通过发现点击不同页码页面URL的变化可以发现，index后面的数字表示页码，所以利用循环实现多页面的多线程爬虫，创建主函数，创建线程池，循环爬取1-9页的网站。

## 文件结构：
xinwen.csv : 运行代码后获得新闻数据，包含标题、时间、来源、新闻内容、责任编辑、新闻网址、图片链接、视频链接。

数据抓取多线程代码.py ：完整代码
