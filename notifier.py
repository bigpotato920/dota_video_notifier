import urllib2
import re
import gzip
import StringIO
from datetime import date
import smtplib
from email.mime.text import MIMEText

class Crawler:

	def __init__(self, url, filename):

		self.url = url
		self.dict = {}

		self.read_config(filename)

	
	def read_config(self, filename):
		"""
		Read cofiguration from file

		Args:
			filename(): Filename of the configuration file
		"""
		file = open(filename)
		while True:
			line = file.readline()
			if not line:
				break
			(key, value) = line.split()
			if key == 'user':
				self.user = value
			elif key == 'password':
				self.pwd = value
			elif key == 'targetlist':
				self.target = value

		file.close()

	def get_page(self, url):

		"""
		Get the content of a web page, judge whether the webserver use gzip to 
		compress the web page, because the urllib2 library doesn't just whether
		the server compress the page or not 

		Args:
			url (str): Url of the target web page

		Returns:
			str: Content of the webpage
		"""
		f = urllib2.urlopen(url)
		headers = f.info()
		rawdata = f.read()

		if ('content-Encoding' in headers and headers['Content-Encoding']) or \
			('content-encoding' in headers and headers['content-encoding']):
			data = StringIO.StringIO(rawdata)
			gz = gzip.GzipFile(fileobj=data)
			content = gz.read()
			gz.close()

			return content
		return rawdata

	def build_dict(self, content):
		"""
		Try to extract the title and the date of the update from the webpage using 
		regular expression,build a dictionary to audit the title and date, namely 
		(title, date) pairs

		Args:
			content (str): Content of the webpage
		"""
		pattern =  re.compile(r'<em>(.+)</em>')	
		title_pattern = re.compile(r'(.+)<br')
		date_pattern = re.compile(r'.+(\d{4}/\d{2}/\d{2})</font>')
		
		items =  pattern.findall(content)

		for item in items:
		
			title_match = re.match(title_pattern, item)
			date_match = re.match(date_pattern, item)

			if (title_match and date_match):
				self.dict[title_match.group(1)] = date_match.group(1)
				

	def check_update(self):
		"""
		Check whether the content of the webpage is an update
		"""
		today = self.get_date_str()
		msg = ''
		for (title, date) in self.dict.items():
			if date == today:
				msg += title + '\n'
				
		print msg
		self.notify(msg)		
		self.dict.clear()
				
	def notify(self, msg):
		"""
		Notify the registered user there is an update through email

		Args:
			msg (str): Message to send to the target user
		"""
		self.email.send_email(self.user, self.pwd, msg, self.target)
  
	
	def get_date_str(self):
		"""
		Get the date string of today for example: 2014/12/05

		Returns:
			str: Date string of today following the format: %Y/%m/%d
		"""
		today = date.today()
		return today.strftime("%Y/%m/%d")


	def start(self):
		"""
		Start the service of the program
		"""
		self.email = Email()
		content = self.get_page(self.url)
		self.build_dict(content)
		self.check_update()



		   		

class Email():

	def __init__(self):
		pass

	def send_email(self, user, pwd, msg, target):
		"""
		Send an email to the target user

		Args:
			user (str): Account name of the sender
			pwd (str): Password of the sender account
			msg (str): Message send to the target user
			target (str): Account of the target user
		"""
		msg = MIMEText(msg)
		msg["Subject"] = "dota update"
		msg["From"] = user
		msg["To"] = target

		s = smtplib.SMTP("smtp.sina.com.cn", timeout=30)
		s.login(user, pwd)
		s.sendmail(user, target, msg.as_string())
		s.close()


target_url = "http://dota.178.com/video/"
filename = "config.txt"

crawler = Crawler(target_url, filename)
crawler.start()

