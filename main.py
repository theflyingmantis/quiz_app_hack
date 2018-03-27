import pyscreenshot as ImageGrab
import pytesseract
from textblob import TextBlob
import sys
from sys import argv
from PIL import Image
import requests
from io import BytesIO
from lxml import html
from bs4 import BeautifulSoup
from collections import Counter
from string import punctuation
import threading
import time
import os
from os.path import expanduser
from quiz_Spider import quizSpider
from scrapy.crawler import CrawlerProcess
import logging
from nltk.corpus import stopwords
stopWords = set(stopwords.words('english'))
from nltk.stem.lancaster import LancasterStemmer
st = LancasterStemmer()



class myThread (threading.Thread):
	def __init__(self, link):
		threading.Thread.__init__(self)
		self.link = link

	def run(self):
		r = requests.get(self.link)
		soup = BeautifulSoup(r.text.encode('utf-8'),'lxml')
		text_p = (''.join(s.findAll(text=True))for s in soup.findAll('p'))
		c_p = Counter((x.rstrip(punctuation).lower() for y in text_p for x in y.split()))
		text_div = (''.join(s.findAll(text=True))for s in soup.findAll('div'))
		c_div = Counter((x.rstrip(punctuation).lower() for y in text_div for x in y.split()))
		total = c_div + c_p
		final_total.append(total)


class Dimensions:
	def loco(self):
		with open('loco_dimensions.txt','r') as f:
			questionDimensions=[int(x.strip()) for x in f.readline().split(',')]
			option1Dimensions=[int(x.strip()) for x in f.readline().split(',')]
			option2Dimensions=[int(x.strip()) for x in f.readline().split(',')]
			option3Dimensions=[int(x.strip()) for x in f.readline().split(',')]
			return {
			'question':questionDimensions,
			'option1':option1Dimensions,
			'option2':option2Dimensions,
			'option3':option3Dimensions
			}

	def hq(self):
		with open('hq_dimensions.txt','r') as f:
			questionDimensions=[int(x.strip()) for x in f.readline().split(',')]
			option1Dimensions=[int(x.strip()) for x in f.readline().split(',')]
			option2Dimensions=[int(x.strip()) for x in f.readline().split(',')]
			option3Dimensions=[int(x.strip()) for x in f.readline().split(',')]
			return {
			'question':questionDimensions,
			'option1':option1Dimensions,
			'option2':option2Dimensions,
			'option3':option3Dimensions
			}


class Game:
	def getScreenshotImage(self,folderPath):
		response=requests.get('http://127.0.0.1:35554/device/2945105d0204/screenshot-test.jpg')
		img = Image.open(BytesIO(response.content))
		filename = folderPath+'/screenshot-'+str(sys.argv[1])+'.jpg'
		img.save(filename)
		return img

	def cropImage(self,im,dimensions,folderPath):
		img=im.crop((dimensions[0],dimensions[1],dimensions[2],dimensions[3]))
		filename = folderPath+'/crop-'+str(sys.argv[1])+str(dimensions[1])+'.jpg'
		img.save(filename)
		return img

	def ocr(self,im):
		text = pytesseract.image_to_string(im, lang = 'eng')
		cleanOcr = " ".join(text.split())
		cleanOcrNlp = TextBlob(cleanOcr)
		return cleanOcrNlp.correct()

	def cleanOptions(self,answerText):
		dirtyOptions = answerText.split('\n')
		cleanOptions = []
		for op in dirtyOptions:
			if op != '':
				b=TextBlob(op)
				cleanOptions.append(b.correct())

	def runSpider(self,question,options,startTime):
		logging.getLogger().setLevel(logging.INFO)
		process = CrawlerProcess({
		    'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36',
		    'LOG_LEVEL' : 'INFO'
		})
		q=str(question.replace(' ','+'))
		URL='https://google.co.in/search?q='+q
		process.crawl(quizSpider,start_urls = [URL],options=options,time=startTime)
		process.start()

	def getAnswer(self, dictionary, op1, op2, op3):
		option1 = self.getSubWords(op1)
		option2 = self.getSubWords(op2)
		option3 = self.getSubWords(op3)
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
			return 'a'
		if final2Count>final1Count and final2Count>final3Count:
			return 'b'
		if final3Count>final1Count and final3Count>final2Count:
			return 'c'
		else: return "None"
		
	def getSubWords(self,op):
		ans = []
		for k in op.split(' '):
			for s in k.split('-'):
				if s not in stopWords:
					ans.append(st.stem(s))
					ans.append(s)
		return ans
		
gamesDimension = {
	'loco':Dimensions().loco,
	'hq':Dimensions().hq
}

# def getScreenshot():
# 	im = Image.open('screenshot-loco.jpg')
# 	return im


if __name__=="__main__":
	startTime=time.time()
	folderPath = expanduser('~/Documents/hacking/quiz_apps/app/images/')+str(argv[1])+'/'+str(time.time())
	if not os.path.isdir(folderPath):
		os.makedirs(folderPath)
	im = Game().getScreenshotImage(folderPath)
	# im = getScreenshot()
	game = sys.argv[1]
	questionDimension = gamesDimension[game]()['question']
	option1Dimension = gamesDimension[game]()['option1']
	option2Dimension = gamesDimension[game]()['option2']
	option3Dimension = gamesDimension[game]()['option3']
	
	
	questionImage = Game().cropImage(im,questionDimension,folderPath)
	option1Image = Game().cropImage(im,option1Dimension,folderPath)
	option2Image = Game().cropImage(im,option2Dimension,folderPath)
	option3Image = Game().cropImage(im,option3Dimension,folderPath)

	questionText = Game().ocr(questionImage).lower()
	option1Text = Game().ocr(option1Image).lower()
	option2Text = Game().ocr(option2Image).lower()
	option3Text = Game().ocr(option3Image).lower()

	# questionText = "which kind of shoe gets its name from a weapon"
	# option1Text = 'boots'
	# option2Text = 'stilettos'
	# option3Text = 'espandrilles'
	print questionText
	
	options=[]
	opt1 = Game().getSubWords(option1Text)
	opt2 = Game().getSubWords(option2Text)
	opt3 = Game().getSubWords(option3Text)
	options.append(opt1)
	options.append(opt2)
	options.append(opt3)
	Game().runSpider(questionText,options,startTime)