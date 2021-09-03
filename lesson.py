'''
Author: XF
Date: 2021-09-02 20:08:33
LastEditTime: 2021-09-04 07:55:17
LastEditors: XF
Description: 
FilePath: \\undefinedc:\\Users\\xf\\Desktop\\BuptMasterClass\\BuptMasterClass\\xyw.py
'''
from bs4 import BeautifulSoup
import time
import requests
import re
import threading
import schedule
import time
import datetime
header = {}

# 新时代中国特色社会主义理论与实践13班
# 研究生英语国际学术交流8班

ids = [["3311101694","研究生英语国际学术交流8班"], ["3321101666","新时代中国特色社会主义理论与实践13班"]] #[[id, 班级或上课时间], ...]
def login(cookiestr):
    global header
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Host": "yjxt.bupt.edu.cn",
        "Referer": "http://yjxt.bupt.edu.cn/Gstudent/leftmenu.aspx?UID=",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": cookiestr
    }
    return header



def get_class_page(header, serverid = 0):

    list_url = f'http://10.3.255.3{serverid}/Lesson/PlanCourseOnlineSel.aspx'
    req = requests.get(list_url, headers=header)
    soup = BeautifulSoup(req.text, 'lxml').find_all('tr', onmouseout="SetRowBgColor(this,false)" )
    return soup


def xuanke(html,id, serverid = 0):
    global ids
    res = re.findall(r'EID=(.*?)\'', html)
    if len(res)==0:
        print("没找到EID")
        return False
    eid = res[0].replace('==', '%3d%3d')
    class_url = f'http://10.3.255.3{serverid}/Lesson/PlanSelClass.aspx?EID={eid}'

    req = requests.get(class_url, headers=header)
    source = req.text

    __EVENTVALIDATION = re.findall(r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)" />', source)[0]
    __VIEWSTATE = re.findall(r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)"', source)[0]

    soup = BeautifulSoup(source, 'lxml').find_all('tr', onmouseout="SetRowBgColor(this,false)" )
    for _,s in enumerate(soup):
        if id[1] in str(s):
            print(id[1])
            print(str(s))
            __EVENTTARGET = re.findall(r"__doPostBack\('(.*?)',", str(s))[0]
    
    if __EVENTTARGET == None:
        print("选课失败!!!")
        return
    payload = {
        'ctl00$ScriptManager1':'ctl00$contentParent$UpdatePanel2|' + __EVENTTARGET,
        'ctl00$contentParent$drpXqu$drpXqu':'',
        '__VIEWSTATEGENERATOR' : 'BD5D4783',
        '__VIEWSTATEENCRYPTED' :'',
        '__VIEWSTATE':__VIEWSTATE,
        '__LASTFOCUS':'',
        '__EVENTVALIDATION':__EVENTVALIDATION,
        '__EVENTTARGET': __EVENTTARGET,
        '__EVENTARGUMENT':'',
        '__ASYNCPOST':'true'
    }

    req = requests.post(class_url, headers=header, data=payload)
    if 'frameElement.api.close()' in req.text:
        print("选课成功")
        ids.remove(id)
        return True
    else:
        print("选课失败")
        return False

if __name__ == "__main__":
    target_time = time.mktime(time.strptime("2021-9-4 7:59:00", "%Y-%m-%d %H:%M:%S"))

    header = login("cookies") #这里需要修改
    counter = 1
    while True:
        now = time.time()
        if now > target_time:
            break
        time.sleep(0.5)
    print("running")
    while True:
        print(counter)
        classes = get_class_page(header)

        if len(ids) == 0:
            print('选课完成')
            break
        
        tmp_ids = []
        tmp_ids.extend(ids)
        for id in tmp_ids:
            for s in classes:
                html = str(s)
                if id[0] in html:
                    if '正在选课' in html:
                        threading.Thread(target=xuanke, args=(html,id,)).start()
                        # xuanke(html)
                    else:
                        print('无法选课 {}'.format(id[1]))
                        break
                    break
            else:
                print('课程id不存在 {}'.format(id[1]))
                # ids.remove(id)
        time.sleep(0.5)
        counter += 1

