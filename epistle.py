'''Written by: loganfynne'''
from email.parser import HeaderParser
import imaplib, smtplib, email
import tweepy, facebook
import re

objects = {}

class Account(dict):
	''' This function is responsible for adding and removing account information used in Epistle. '''
	#def __init__(self, objects):
	#	''' Initializes variables for the class.'''
	#	self.objects = objects

	def gmail(self):
		''' This function logs the user into their Gmail account. '''
		global objects
		objects['gmailuser'] = raw_input('What is your email username: ')
		password = raw_input('What is your email password: ')

		objects['imapmail'] = imaplib.IMAP4_SSL('imap.gmail.com', 993)
		auth, logged = objects['imapmail'].login(objects['gmailuser'], password)
		print auth, logged

		objects['smtpmail'] = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		auth, logged = objects['smtpmail'].login(objects['gmailuser'], password)
		print auth, logged

	def facebook(self):
		''' This function logs the user into their Facebook account. '''
		global objects
		objects['Facebook'] = facebook.Facebook('967f7407da4bc19095c5bcc94b5375ac', '84a11f3e972a9c94034af84a3b87cfe0')

		objects['Facebook'].auth.createToken()
		objects['Facebook'].login(popup=True)

		raw_input('After logging in, press enter...')
		objects['Facebook'].auth.getSession()
		objects['Facebook'].request_extended_permission('read_stream')
		objects['Facebook'].request_extended_permission('publish_stream')
		raw_input('After logging in, press enter...')
		print 'Login successful.'
		print 'Session Key: ', objects['Facebook'].session_key
		print 'Your UID:    ', objects['Facebook'].uid

	def twitter(self):
		''' This function logs the user into their Twitter account. '''
		global objects
		auth = tweepy.OAuthHandler('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
		auth.set_request_token('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
		auth_url = auth.get_authorization_url()
		print 'Please authorize: ', auth_url
		pin = raw_input('PIN: ')
		auth.get_access_token(pin)
		print 'access_key = ', auth.access_token.key
		print 'access_secret = ', auth.access_token.secret
		objects['Twitter'] = tweepy.API(auth)
		print objects['Twitter']

class Epistle(dict):
	''' This is the main application class. '''
	#def __init__(self, objects):
	#	''' Initializes variables for the class.'''
	#	self.objects = objects
		
	def readmail(self):
		''' This function reads unread messages from Gmail. '''
		global objects
		selectlabel = objects['imapmail'].select('Inbox')
		print ('Inbox: ', selectlabel[1])
		numinbox = re.split('', str(selectlabel[1]))
		numinbox = '0-9'.join(numinbox)
		x = 0
		addto = []
		while x < len(numinbox):
			if numinbox[x].isdigit(): addto.append(numinbox[x])
			x = x + 1
		numinbox = ''.join(addto)
		numinbox = int(numinbox)

		unread = objects['imapmail'].status('Inbox', '(UNSEEN)')
		print 'Unread: ', unread

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

		for x in range((numinbox - numunread),numinbox):
			resp, data = objects['imapmail'].FETCH(x, '(RFC822)')
			message = HeaderParser().parsestr(data[0][1])
			print '\n\n'
			print 'From: ', message['From']
			print 'To: ', message['To']
			print 'Subject: ', message['Subject'], '\n\n'

			mailitem = email.message_from_string(data[0][1])

			for mailpart in mailitem.walk():
				if mailpart.get_content_maintype() == 'multipart':
					continue
					
				if mailpart.get_content_subtype() != 'plain':
					continue
					
				message = mailpart.get_payload()
		  		print (message)

	def sendmail(self):
		global objects
		''' This function sends an email using Gmail. '''
		choice = raw_input('Send email message(1)? ')
		if choice == '1':
			to = raw_input('To: ')
			subject = raw_input('Subject: ')
			mailmessage = raw_input('Message: ')
			objects['smtpmail'].sendmail(objects['gmailuser'], to, 'Subject: ', subject, '\n', mailmessage)

	def updatetwitter(self):
		''' This function updates the user's Tweets. '''
		twitterupdate = objects['Twitter'].home_timeline()
		for x in range(0,19):
			print twitterupdate[x].text, '\n'

	def posttwitter(self):
		global objects
		''' This function posts a Tweet. '''
		print objects
		tweet = raw_input('Update Twitter: ')
		if len(tweet) >= 140:
			while (len(tweet) >= 140):
				print('The character limit of 140 was exceeded.')
				tweet = raw_input('Update Twitter: ')
		objects['Twitter'].update_status(tweet)

	def updatefb(self):
		global objects
		''' This function updates the Facebook stream. '''
		objects['Facebook'].stream.get()

	def postfb(self):
		global objects
		''' This function posts to Facebook. '''
		fbstatus = raw_input('Set your Facebook status: ')
		objects['Facebook'].status.set(fbstatus)

	def main(self):
		''' This function will include the interface of Epistle, and all the function calls. '''
		global objects
		pass

#Account().gmail()
Account().twitter()
#Account().facebook()
#Epistle(objects).updatetwitter(objects)
Epistle().posttwitter()
#objects['imapmail'].logout()
#objects['smtpmail'].quit()
#imapmail.logout()
#smtpmail.quit()