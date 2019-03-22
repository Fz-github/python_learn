from wordcloud import WordCloud,ImageColorGenerator
import jieba
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from PIL import Image
import numpy as  np
from mysql import MySQL

mysql = MySQL()

#stopwords.txt文件路径 
stopwords_path='stopwords/baidu_stopwords.txt'
#背景图
bg=np.array(Image.open("reptile/WechatSpider/xin.jpg")) 

def get_comment_txt():
    content_txt = ''
    lists = mysql.select_all('zongmeng')
    i= 0
    for row in lists:
        if "表白墙" in row[1]:
            content_txt += row[2]
            i+=1
        
    print("共%d期"%i)
            
    
    
    return content_txt

    

def jiebaclearText():
    comment_txt = get_comment_txt()
    word_list=[]
    # 使用jieba分词
    seg_list = jieba.cut(comment_txt.replace('\n','').replace(' ',''))
    #将一个generator的内容用/连接
    listStr='/'.join(seg_list)
    #读取停用词列表
    with open(stopwords_path,'r',encoding='utf8') as f:
        stopwords_str = f.read()
    stopwords_list = stopwords_str.split('\n')
    stopwords_list.append('表白')
    # stopwords_list.append('唯有')
    # stopwords_list.append('之间')
    # stopwords_list.append('凡是')
    # stopwords_list.append('明白')
    # stopwords_list.append('世间')
    # stopwords_list.append('回家')
    # stopwords_list.append('农产品')
    # stopwords_list.append('例外')
    # stopwords_list.append('欢迎')
    # stopwords_list.append('鼎力支持')
    # stopwords_list.append('赣州')
    # stopwords_list.append('男排')
    # stopwords_list.append('凡事')
    # stopwords_list.append('市场')
    # stopwords_list.append('价格比')
    # stopwords_list.append('欢迎')
    # stopwords_list.append('交易中心')
    
    
    #对默认模式分词的进行遍历，去除停用词
    for myword in listStr.split('/'):
        #去除停用词
        if not myword in stopwords_list and len(myword.strip())>1:
            word_list.append(myword)
    return ' '.join(word_list)

    


# 生成词云
def get_wordCloud ():
    text = jiebaclearText()
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
    wc.to_file("zongmeng.png")

get_wordCloud()