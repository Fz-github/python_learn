# coding:utf-8

from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from wordcloud import WordCloud,ImageColorGenerator
import jieba
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from PIL import Image
import numpy as  np

# monogo数据库连接
client = MongoClient(host = "148.70.61.218",port = 27017)
db = client['douban']
collection = db['dbxj_comment']

#爬虫
base_url = "https://movie.douban.com/subject/30397901/comments?"
headers = {
    'Cookie':'''bid=rY6tAM7uChQ; douban-fav-remind=1; ll="108120"; _vwo_uuid_v2=D554F89E66C2D8514FFA212FCAEBFA828|8189ffa81fd203b1988be742f387c932; gr_user_id=a47aa0b3-c7ed-4094-9ec7-eef4c003ceb0; viewed="25723796_6025284_26590145_26702570"; __utmc=30149280; __utmz=30149280.1551366678.7.5.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmc=223695111; __utmz=223695111.1551366898.3.2.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/search; __utma=223695111.1561671859.1550670417.1551404794.1551408211.5; regpop=1; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1551412035%2C%22https%3A%2F%2Fwww.douban.com%2Fsearch%3Fq%3D%25E6%2598%2593%25E7%2583%258A%25E5%258D%2583%25E7%258E%25BA%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.1220415505.1548237601.1551408211.1551412035.10; __utmt=1; ap_v=0,6.0; __utmb=30149280.10.9.1551412191672; _pk_id.100001.4cf6=3f6995ce758fac8b.1550670417.6.1551412203.1551409785.; dbcl2="192603558:v4iTjVQFyEU"; ck=sRsb''',
    'Host': "movie.douban.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
    'X-Requested-With': "XMLHttpRequest",
}
#爬虫url的参数
params={
        'start' :0,
        'limit':20,
        'sort':"time",
        'status':"P",
        'comments_only':1,
    }

# 词云
## 添加需要自定以的分词
jieba.add_word("易烊千玺")
jieba.add_word("雷佳音")

#stopwords.txt文件路径 
stopwords_path='stopwords/baidu_stopwords.txt'
#背景图
bg=np.array(Image.open("yyqx.png")) 



def get_page(page):
    params['start'] = page*20
    url = base_url + urlencode(params)
    response = requests.get(url,headers = headers)
    if response.status_code == 200:
        result = response.json()
        return result.get('html')
    
def parse_page(html):
    soup = BeautifulSoup(html,'lxml')
    pl_items = soup.find_all(attrs={'class':"comment-item"})
    for pl_item in pl_items:
        if  pl_item.find(attrs={'class':"rating"}):
            rate = convert_rate(pl_item.find(attrs={'class':"rating"})['title'])
        else:
            rate = 0  
        comment_item = {
            'user': pl_item.find(attrs={'class':"avatar"}).a['title'],
            'time': pl_item.find(attrs={'class':"comment-time"})['title'],
            'rate': rate,
            'comment': pl_item.find(attrs={'class':"short"}).string,
        }
        yield comment_item

def convert_rate(str):
    rates={
        '力荐':5,
        '推荐':4,
        '还行':3,
        '较差':2,
        '很差':1,
    }
    return rates.get(str,0)        

def get_data():
    i = 0
    while True:
        html = get_page(i)
        if html.find("还没有人写过短评") == -1:
            results = parse_page(html)
            for result in results:
                collection.insert_one(result)
            i+=1
            print("正在进行第"+str(i)+"次爬取最新的评论")
        else:
            print("完成所有最新评论的爬取")
            break

    percent_types = ['h','m','l']
    params['sort']= 'new_score'
    
    for percent_type in percent_types:
        params['percent_type'] = percent_type
        i=0
        while True:
            html = get_page(i)
            if html.find("还没有人写过短评") == -1:
                results = parse_page(html)
                for result in results:
                    collection.insert_one(result)
                i+=1
                print("正在进行第"+str(i)+"次爬取%s的评论"%percent_type)
            else:
                print("完成所有%s评论的爬取"%percent_type)
                break

# 从数据中读取comment字段的所有值，并拼成一个字符串
def get_comment_txt():
    try:
        comment_list =collection.find({},{"comment":1,"_id":0})
        comment_txt=""
        for comment in comment_list:
            comment_txt += comment['comment']
        return comment_txt
    except:
        print("error")

def jiebaclearText(comment_txt):
    word_list=[]
    # 使用jieba分词
    seg_list = jieba.cut(comment_txt.replace('\n','').replace(' ',''))
    #将一个generator的内容用/连接
    listStr='/'.join(seg_list)
    #读取停用词列表
    with open(stopwords_path,'r',encoding='utf8') as f:
        stopwords_str = f.read()
    stopwords_list = stopwords_str.split('\n')
    
    #对默认模式分词的进行遍历，去除停用词
    for myword in listStr.split('/'):
        #去除停用词
        if not(myword.split()) in stopwords_list and len(myword.strip())>1:
            word_list.append(myword)
    return ' '.join(word_list)

    


# 生成词云
def get_wordCloud (text):
    wc=WordCloud(
        background_color="white", 
        max_words=200,
        mask=bg,            #设置图片的背景
        max_font_size=60,
        random_state=42,
        font_path='C:/Windows/Fonts/simkai.ttf'   #中文处理，用系统自带的字体
        ).generate(text)
    #为图片设置字体
    my_font=fm.FontProperties(fname='C:/Windows/Fonts/simkai.ttf')
    #产生背景图片，基于彩色图像的颜色生成器
    image_colors=ImageColorGenerator(bg)
    #开始画图
    plt.imshow(wc.recolor(color_func=image_colors))
    #为云图去掉坐标轴
    plt.axis("off")
    #画云图，显示
    plt.figure()
    #为背景图去掉坐标轴
    plt.axis("off")
    plt.imshow(bg,cmap=plt.cm.gray)

    #保存云图
    wc.to_file("dbxj.png")


if __name__ == "__main__":
    # get_data()
    comment_txt = get_comment_txt()
    text = jiebaclearText(comment_txt)
    get_wordCloud(text)


    

        