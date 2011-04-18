'''Written by: loganfynne'''
from email.parser import HeaderParser
import imaplib, smtplib, email
import facebooksdk, tweepy
#import gtk, gobject, 
import re, webkit

def gmail():
	''' Collect data for Gmail.'''
	gmailuser = raw_input('What is your email username: ')
	password = raw_input('What is your email password: ')
	returned = {'gmailuser':gmailuser, 'password':password}
	return returned
def twitter():
	''' Collect data for Twitter.'''
	auth = tweepy.OAuthHandler('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
	auth.set_request_token('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
	auth_url = auth.get_authorization_url()
	print 'Please authorize: ', auth_url
	pin = raw_input('PIN: ')
	auth.get_access_token(pin)
	#print 'access_key = ', auth.access_token.key
	#print 'access_secret = ', auth.access_token.secret
	returned = {'auth':auth}
	return returned

def facebook():
	'''Collect data for Facebook.'''
	pass

class Account:
	''' This function is responsible for adding and removing account information used in Epistle. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)
		self.Gmail = gmail()
		#self.Twitter = twitter()
		#self.Facebook = facebook()

	def gmail(self):
		''' This function logs the user into their Gmail account. '''
		self.Gmail['imap'] = imaplib.IMAP4_SSL('imap.gmail.com', 993)
		self.Gmail['smtp'] = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		return self.Gmail
		
	def twitter(self):
		''' This function logs the user into their Twitter account. '''
		self.Twitter['Twitter'] = tweepy.API(self.Twitter['auth'])
		return self.Twitter

	def facebook(self):
		''' This function logs the user into their Facebook account. '''
		self.Facebook['Facebook'] = facebooksdk.GraphAPI(self.Facebook['auth'])
		self.Facebook['profile'] = self.Facebook['Facebook'].get_object('me')
		self.Facebook['friends'] = self.Facebook['Facebook'].get_connections('me', 'friends')
		return self.Facebook

class Epistle:
	''' This is the main application class. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)
		self.Gmail = Account().gmail()
		#self.Twitter = Account().twitter()
		#self.Facebook = Account().facebook()

	def readmail(self):
		''' This function reads unread messages from Gmail. '''
		self.Gmail['imap'].login(self.Gmail['gmailuser'], self.Gmail['password'])

		selectlabel = self.Gmail['imap'].select('Inbox')
		numinbox = re.split('', str(selectlabel[1]))
		numinbox = '0-9'.join(numinbox)
		x = 0
		addto = []
		while x < len(numinbox):
			if numinbox[x].isdigit(): addto.append(numinbox[x])
			x = x + 1
		numinbox = ''.join(addto)
		numinbox = int(numinbox)

		unread = self.Gmail['imap'].status('Inbox', '(UNSEEN)')

		unread = str(unread)
		numunread = re.split('', unread)
		numunread = '0-9'.join(numunread)

		x = 0
		addto = []
		while x < len(unread):
			if unread[x].isdigit(): addto.append(numunread[x])
			x = x + 1
		numunread = ''.join(addto)
		numunread = int(numunread)

		for x in range(((numinbox - numunread)),numinbox):
			resp, data = self.Gmail['imap'].FETCH(x, '(RFC822)')
			message = HeaderParser().parsestr(data[0][1])
			print '\n\n'
			print 'From: ', message['From']
			print 'To: ', message['To']
			print 'Subject: ', message['Subject'], '\n\n'

			mailitem = email.message_from_string(data[0][1])

			for mailpart in mailitem.walk():
				if mailpart.get_content_maintype() == 'multipart':
					continue
					
				if mailpart.get_content_subtype() == 'html':
					message = mailpart.get_payload()
					print message
				
				if mailpart.get_content_subtype() == 'text':
					message = mailpart.get_payload()
					print message
		self.Gmail['imap'].logout()

	def sendmail(self):
		''' This function sends an email using Gmail. '''
		self.Gmail['smtp'].login(self.Gmail['gmailuser'], self.Gmail['password'])
		to = raw_input('To: ')
		subject = raw_input('Subject: ')
		mailmessage = raw_input('Message: ')
		self.Gmail['smtp'].sendmail(self.Gmail['gmailuser'], to, 'Subject: ' + subject + '\n' +mailmessage)
		self.Gmail['smtp'].quit()
	def updatetwitter(self):
		''' This function updates the user's Tweets. '''
		twitterupdate = self.Twitter['Twitter'].home_timeline()
		for x in range(0,19):
			print twitterupdate[x].user.screen_name, ' : ', twitterupdate[x].text, '\n'

	def posttwitter(self):
		''' This function posts a Tweet. '''
		tweet = raw_input('Update Twitter: ')
		if len(tweet) >= 140:
			while (len(tweet) >= 140):
				print('The character limit of 140 was exceeded.')
				tweet = raw_input('Update Twitter: ')
		self.Twitter['Twitter'].update_status(tweet)

	def updatefb(self):
		''' This function updates the Facebook stream. '''
		pass

	def postfb(self):
		''' This function posts to Facebook. '''
		fbstatus = raw_input('Set your Facebook status: ')
		self.Facebook['Facebook'].put_object("me", "feed", message=fbstatus)

	def main(self):
		''' This function will include the interface of Epistle, and all the function calls. '''
		pass

if __name__ == '__main__':
	app = Epistle()
	app.readmail()
	#app.sendmail()
	#app.updatetwitter()
	#app.posttwitter()
	#app.updatefb()
	#app.postfb()