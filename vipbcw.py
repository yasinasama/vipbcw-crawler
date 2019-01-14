import requests
from bs4 import BeautifulSoup

import queue
import re
import sys
import os
import threading

class S:
    URL = 'http://in.vipbcw.com/user.php'
    URL2 = 'http://in.vipbcw.com/category.php?id=6'
    def __init__(self,username,password):
        self.timeout = 10
        self.session = requests.Session()
        self.text = None
        self.params = {
            'act':'act_login',
            'username':username,
            'password':password
        }

    def login(self):
        try:
            self.session.post(self.URL,data=self.params,timeout=self.timeout)
            self.text = self.session.get(self.URL2,timeout=self.timeout).text
        except:
            raise
        finally:
            self.session.close()
        return self.session


class Category:
    def __init__(self,text,queue):
        self.host = 'http://in.vipbcw.com/'
        self.pattern = '(category.php\?id=\d+)'
        if text is None:
            print('text not exist')
            sys.exit()
        self.text = text
        self.queue = queue

    def extract_url(self):
        return re.findall(self.pattern,self.text)

    def append_url(self):
        r = self.extract_url()
        for i in r:
            curl = self.host+i
            self.queue.put(curl)


class Crawler:
    def __init__(self,session,queue,fp):
        self.session = session
        self.timeout = 10

        self.queue = queue
        self.thread_num = 5

        self.fp = fp        
        self.lock = threading.Lock()

    def download(self,url):
        res = self.session.get(url,timeout=self.timeout)
        soup = BeautifulSoup(res.text,'lxml')
       
        ul = soup.find(class_='pro_ul_list')
        if ul:
            li_list = ul.find_all('li')
            for li in li_list:
                try:
                    # proid = re.findall('(\d+)',li.find_all('p')[0].a['href'])[0]
                    proname = li.find_all('p')[0].a.text
                    proprice = li.find_all('p')[1].text
                    with self.lock:
                        self.fp.write('%s, %s, %s'%(url,proname,proprice))
                        print(proname)
                        self.fp.write('\n')
                except:
                    pass

    def do(self):
        while not self.queue.empty():
            url = self.queue.get()
            self.download(url)
            self.queue.task_done()

    def run(self):
        l = []
        for _ in range(self.thread_num):
            t = threading.Thread(target=self.do)
            l.append(t)

        for i in l:
            i.start()

        for i in l:
            i.join()

        self.queue.join()

def main():
    fname = './data.txt'
    if os.path.exists(fname):
        os.remove(fname)
    f = open(fname,'w')
    username = input('>>> username: ')
    password = input('>>> password: ')
    Q = queue.Queue()
    s = S(username,password)
    session = s.login()
    text = s.text
    c = Category(text,Q)
    c.append_url()
    hi = Crawler(session,Q,f)
    hi.run()
    f.close()
    


if __name__=='__main__':
    main()
    
    