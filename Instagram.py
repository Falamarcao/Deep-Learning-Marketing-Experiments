# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 21:28:27 2018

@author: Falamarcao
"""

#import re
#from time import sleep
from time import sleep
from tqdm import trange
from requests import Session
from bs4 import BeautifulSoup
from selenium import webdriver
#from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from os import makedirs, chdir#, listdir
from os.path import exists, dirname, basename


class Instagram(object):

    def __init__(self, hashtag, is_profile = False):
        self.hashtag = hashtag
        self.imgLinks = []
        self.is_profile = is_profile
        
        if self.is_profile:
            self.url = "https://www.instagram.com/" + self.hashtag
        else:
            self.url = "https://www.instagram.com/explore/tags/" + self.hashtag
        self.webdriver = webdriver

        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/62.0.3202.94 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}

        #Download Folder
        chrome_options = self.webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")

        #WEB BROWSER - CHROME
        executable_path = r'C:\Users\Falamarcao\Anaconda3\selenium\webdriver\chrome\chromedriver.exe'
        self.browser =  self.webdriver.Chrome(executable_path, chrome_options=chrome_options)
        self.browser.get(self.url)

    def scroll(self, seconds):

        self.browser.execute_script("window.scrollTo(0,1000000)")
        
        #load more
        if self.is_profile:
            xpath = '//*[@id="react-root"]/section/main/article/div/a'
        else: 
            xpath = '//*[@id="react-root"]/section/main/article/div[2]/a'
        
        element_present = EC.presence_of_element_located((By.XPATH, xpath))
        WebDriverWait(self.browser, 10).until(element_present)
        
        self.browser.find_element_by_xpath(xpath).send_keys("\n")
        
        #scroll
        print("Scrolling...")
        for n in range(seconds):
            self.browser.execute_script("window.scrollTo(0,1000000)")
            sleep(1)
        
        print("Scroll Step has completed")     


    def collect(self):
        bs = BeautifulSoup(self.browser.page_source, "html.parser")
        #self.imgLinks = [link for link in [tag.get('src') for tag in bs.findAll('img')] if link[-3:] == 'jpg']
        self.imgLinks = [tag.get('src') for tag in bs.findAll('img')]
        print("Link were collected")
        
    def download(self):

        if not exists(str(dirname(__file__))+ r'/Data/'+ self.hashtag):
            makedirs(dirname(__file__)+ r'/Data/'+ self.hashtag)

        if basename(dirname(__file__)) != self.hashtag:
            chdir(dirname(__file__) + r'/Data/'+ self.hashtag)

        dSess = Session() #requests library
        print("Downloading images...")
        sleep(5)
        for n, link in enumerate(self.imgLinks, 1):
            if n >= 10:
                strn = '0' + str(n)
            elif n <= 10:
                strn = '00' + str(n)
            else:
                strn = str(n)
            with open(strn + link[-4:], 'wb') as image:
                imgBytes = dSess.get(link, headers=self.headers, stream=True).content
                image.write(imgBytes)
                image.close
                
        dSess.close()
        chdir(dirname(__file__)) # returns to root diretory
        print("Download process completed!")


    def close(self):
        #self.browser.implicitly_wait(10)
        self.browser.quit()
        print( "INSTASCRAPING for hashtag: '"+self.hashtag+"' has finished!\n \
                Please check your files in the folder.")
    
class PllInstagram(Instagram):
    
    def __init__(self, hashtag_list, is_profile = False):
      self.hashtag_list = hashtag_list
      self.is_profile = is_profile
    
    def Instagram_scrapping(self, hashtag):
        b = Instagram(hashtag, self.is_profile)
        b.scroll(2000)
        b.collect()
        b.download()
        b.close()
    
    def start(self):
           
      from multiprocessing import Pool
      
      print('Parallel processing has started...')
      pool = Pool(len(self.hashtag_list))
      self.OutputDataFrame = pool.map(self.Instagram_scrapping, self.hashtag_list)
      pool.close()
      pool.join()
      print('Parallel processing has finished...')
    
    

if __name__ == '__main__':
   PllInstagram(["cocacola", "pepsi", "guaranaantarctica"], is_profile = True).start()
