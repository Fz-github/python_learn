
#使用selenium 爬取四六级成绩

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException,TimeoutException,NoAlertPresentException
from PIL import Image
import io
import requests

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)
#设置显式等待，时间为10秒
wait = WebDriverWait(browser,10)
#打开四立级查询网页
browser.get('http://cet.neea.edu.cn/cet/')

def get_page(zkzh,name):
    '''获取和解析输入页面'''
    #获取准考证输入框并输入准考证号
    zkzh_input = wait.until(EC.presence_of_element_located((By.ID,'zkzh')))
    zkzh_input.send_keys(zkzh)
    #获取姓名输入框并输入姓名
    name_input  = wait.until(EC.presence_of_element_located((By.ID,'name')))
    name_input.send_keys(name)
    #获取验证码输入框，并点击输入框，验证码图片在点击后出现
    verify_input = wait.until(EC.presence_of_element_located((By.ID,'verify')))
    verify_input.click()
    #获取验证码图片
    get_verify_img(verify_input)
    

def get_verify_img(verify_input):
    #获取验证码图片，如果验证码没有出现，即获取网页上的错误提示（准考证号是否准确）    
    try :
        img = wait.until(EC.visibility_of_element_located((By.ID,'img_verifys')))
        url = img.get_attribute('src')
        #通过图片地址获取验证码
        verify = get_verify(url)
        #输入验证码
        verify_input.send_keys(verify)
        
    except TimeoutException:
        em = wait.until(EC.presence_of_element_located((By.ID,'zkzherror')))
        print(em.text)

    #检测验证码是否正确，若出现弹窗，表明验证码错误，则获取弹窗内容；否则，浏览器进入查询结果页面，返回浏览器对象    
    try:
        verify_input.send_keys(Keys.ENTER)
        alert = browser.switch_to.alert
        error_text = alert.text
        print(error_text)
        alert.accept()
        if error_text != "您查询的结果为空！":
            get_verify_img(verify_input)
            
    except NoAlertPresentException:
        get_score(browser)


def get_verify(url):
    """获取验证码"""
    response = requests.get(url)
    #将返回的结果转换成Image对象
    verify_img = Image.open(io.BytesIO(response.content))
    #展示图片让用户输入
    verify_img.show()
    verify = input("请输入验证码：")
    return verify

def get_score(browser):
    '''对查询结果页面进行，获取相关信息'''
    print("#"*5 + "2018年下半年全国大学英语四、六级考试（含口试）成绩查询结果" + "#"*5)
    #获取信息
    cet = browser.find_element_by_id('sn').text
    name = browser.find_element_by_id('n').text
    school = browser.find_element_by_id('x').text
    zkzh =browser.find_element_by_id('z').text
    sum = browser.find_element_by_id('s').text
    listen = browser.find_element_by_id('l').text
    read = browser.find_element_by_id('r').text
    write = browser.find_element_by_id('r').text

    #打印信息
    print(' '*15 + cet)
    print(' '* 19 + "准考证：" + zkzh)
    print(' '* 20 + "学校：" + school)
    print(' '* 20 + "姓名：" + name)
    print(' '* 20 + "总分：" + sum)
    print(' '* 20 + "听力：" + listen)
    print(' '* 20 + "阅读：" + read)
    print(' '* 20 + "写作：" + write)

def main():
    zkzh = input("请输入准考证号：")
    name = input('请输入姓名：')
    get_page(zkzh,name)


    


if __name__ == "__main__":
    while True:
        main()
        print('\n')    
        flag = input("是否继续查询(y/n)：")
        if flag == 'y':
            browser.refresh()
        else:
            break

        
    
    