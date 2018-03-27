from scrapy import signals
from scrapy import Spider
from scrapy.utils.response import open_in_browser
from scrapy.http import FormRequest
import time
import re
from collections import Counter
from string import punctuation
from bs4 import BeautifulSoup


class quizSpider(Spider):
    name = "quiz_Spider"
    def __init__(self, start_urls=None,options=None,time=None,*args, **kwargs):
        self.start_urls=start_urls
        self.options = options
        self.time= time
        self.ans = {
        'a':0,
        'b':0,
        'c':0        }
        super(quizSpider, self).__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(quizSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider


    def spider_closed(self, spider):
        print "\n\n\n",self.ans,"\n\n\n"
        spider.logger.info('Spider closed: %s', spider.name)


    def parse(self, response):
        open_in_browser(response)
        links = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "r", " " ))]//a/@href').extract()
        for link in links:
            yield FormRequest(url=link,callback=self.searchOneLink)

    def searchOneLink(self,response):
        soup = BeautifulSoup(response.body,'lxml')
        # We get the words within paragrphs
        text_p = (''.join(s.findAll(text=True))for s in soup.findAll('p'))
        c_p = Counter((x.rstrip(punctuation).lower() for y in text_p for x in y.split()))

        # We get the words within divs
        text_div = (''.join(s.findAll(text=True))for s in soup.findAll('div'))
        c_div = Counter((x.rstrip(punctuation).lower() for y in text_div for x in y.split()))

        # We sum the two countesr and get a list with words count from most to less common
        dictionary = c_div + c_p
        option1 = self.options[0]
        option2 = self.options[1]
        option3 = self.options[2]
        lcm=len(option1)*len(option2)*len(option3)
        op1Count=0
        op2Count=0
        op3Count=0
        for option in option1:
            op1Count+=dictionary[option]
        for option in option2:
            op2Count+=dictionary[option]
        for option in option3:
            op3Count+=dictionary[option]
        final1Count = op1Count*lcm/len(option1)
        final2Count = op2Count*lcm/len(option2)
        final3Count = op3Count*lcm/len(option3)
        print final1Count,final2Count,final3Count
        if final1Count>final2Count and final1Count>final3Count:
            scaledValue = float(2*final1Count-final2Count -final3Count)/(final1Count+final2Count+final3Count)
            self.ans['a']+=scaledValue
        if final2Count>final1Count and final2Count>final3Count:
            scaledValue = float(2*final2Count-final1Count -final3Count)/(final1Count+final2Count+final3Count)
            self.ans['b']+=scaledValue
        if final3Count>final1Count and final3Count>final2Count:
            scaledValue = float(2*final3Count-final2Count -final1Count)/(final1Count+final2Count+final3Count)
            self.ans['c']+=scaledValue
        # else: self.ans['None']+=1
        if time.time()-self.time>5:
            print self.ans
        

        