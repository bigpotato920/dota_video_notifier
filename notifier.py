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

		rawdata = urllib2.urlopen(url).read()
		data = StringIO.StringIO(rawdata)
		gz = gzip.GzipFile(fileobj=data)
		content = gz.read()
		gz.close()

		return content


	def build_dict(self, content):

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
		today = self.get_date_str()
		msg = ''
		for (title, date) in self.dict.items():
			if date == today:
				msg += title + '\n'
				
				
		print msg
		self.notify(msg)		
		self.dict.clear()
				
	def notify(self, msg):
		
		self.email.send_email(self.user, self.pwd, msg, self.target)
  

	def start(self):

		self.email = Email()
		content = self.get_page(self.url)
		self.build_dict(content)
		self.check_update()


	def get_date_str(self):

		today = date.today()
		return today.strftime("%Y/%m/%d")
		   		

class Email():

	def __init__(self):
		pass

	def send_email(self, user, pwd, msg, target):

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

