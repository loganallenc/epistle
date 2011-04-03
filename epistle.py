'''Written by: loganfynne'''
from email.parser import HeaderParser
import imaplib, smtplib, email
import tweepy, facebook
import re

imapmail = ''
smtpmail = ''

Twitter = ''
Facebook = ''

gmailuser = ''

twitter_key = 'yE6isPwi45JwhEnHMphdcQ'
twitter_secret = '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw'
fb_key = '967f7407da4bc19095c5bcc94b5375ac'
fb_secret = '84a11f3e972a9c94034af84a3b87cfe0'

class Account:
	''' This function is responsible for adding and removing account information used in Epistle. '''
	def gmail(self):
		''' This function logs the user into their Gmail account. '''
		global imapmail
		global smtpmail
		global gmailuser
		gmailuser = raw_input('What is your email username: ')
		password = raw_input('What is your email password: ')

		imapmail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
		auth, logged = imapmail.login(gmailuser, password)
		print (auth, logged)

		smtpmail = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		auth, logged = smtpmail.login(gmailuser, password)
		print (auth, logged)

	def facebook(self):
		''' This function logs the user into their Facebook account. '''
		global fb_key
		global fb_secret
		global Facebook

		Facebook = facebook.Facebook(fb_key, fb_secret)

		Facebook.auth.createToken()
		Facebook.login(popup=True)

		raw_input('After logging in, press enter...')
		Facebook.auth.getSession()
		Facebook.request_extended_permission('read_stream')
		Facebook.request_extended_permission('publish_stream')
		raw_input('After logging in, press enter...')
		print ('Login successful.')
		print ('Session Key:   ', Facebook.session_key)
		print ('Your UID:      ', Facebook.uid)

	def twitter(self):
		''' This function logs the user into their Twitter account. '''
		global twitter_key
		global twitter_secret
		global Twitter
		auth = tweepy.OAuthHandler(twitter_key, twitter_secret)
		auth.set_request_token(twitter_key, twitter_secret)
		auth_url = auth.get_authorization_url()
		print ('Please authorize: ', auth_url)
		pin = raw_input('PIN: ')
		auth.get_access_token(pin)
		print ('access_key = ', auth.access_token.key)
		print ('access_secret = ', auth.access_token.secret)
		Twitter = tweepy.API(auth)

class Epistle:
	''' This is the main application class. '''
	def readmail(self):
		''' This function reads unread messages from Gmail. '''
		global imapmail
		global smtpmail
		global gmailuser
		selectlabel = imapmail.select('Inbox')
		print ('Inbox: ', selectlabel[1])
		numinbox = re.split('', str(selectlabel[1]))
		numinbox = '0-9'.join(numinbox)
		x = 0
		addto = []
		while x < len(numinbox): #Converts number of items in the inbox into an 'int' object.
			if numinbox[x].isdigit(): addto.append(numinbox[x])
			x = x + 1
		numinbox = ''.join(addto)
		numinbox = int(numinbox)

		unread = imapmail.status('Inbox', '(UNSEEN)')
		print ('Unread: ', unread)

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
			resp, data = imapmail.FETCH(x, '(RFC822)')
			message = HeaderParser().parsestr(data[0][1])
			print '\n\n'
			print 'From: ', message['From']
			print 'To: ', message['To']
			print 'Subject: ', message['Subject'], '\n\n'
	
			mailitem = email.message_from_string(data[0][1])
 
			for mailpart in mailitem.walk():
				#print 'Content-Type:', mailpart.get_content_type()
				#print 'Main Content:', mailpart.get_content_maintype()
				#print 'Sub Content:', mailpart.get_content_subtype()
		
				if mailpart.get_content_maintype() == 'multipart':
					continue

				if mailpart.get_content_subtype() != 'plain':
					continue

				message = mailpart.get_payload()
		  		print (message)
	
	def sendmail(self):
		''' This function sends an email using Gmail. '''
		global imapmail
		global smtpmail
		global gmailuser
		choice = raw_input('Send email message(1)? ')
		if choice == '1':
			to = raw_input('To: ')
			subject = raw_input('Subject: ')
			mailmessage = raw_input('Message: ')
			smtpmail.sendmail(gmailuser, to, 'Subject: ', subject, '\n', mailmessage)

	def updatetwitter(self):
		''' This function updates the user's Tweets. '''
		global Twitter
		twitterupdate = Twitter.home_timeline()
		for x in range(0,19):
			print(twitterupdate[x].text, '\n')

	def posttwitter(self):
		''' This function posts a Tweet. '''
		global Twitter
		tweet = raw_input('Update Twitter: ')
		if len(tweet) >= 140:
			while (len(tweet) >= 140):
				print('The character limit of 140 was exceeded.')
				tweet = raw_input('Update Twitter: ')
		Twitter.update_status(tweet)

	def updatefb(self):
		''' This function updates the Facebook stream. '''
		global Facebook
		Facebook.stream.get()

	def postfb(self):
		''' This function posts to Facebook. '''
		global Facebook
		fbstatus = raw_input('Set your Facebook status: ')
		Facebook.status.set(fbstatus)

	def main(self):
		''' This function will include the interface of Epistle, and all the function calls. '''
		pass

#Account().gmail()
Account().twitter()
#Account().facebook()
Epistle().updatetwitter()
#imapmail.logout()
#smtpmail.quit()