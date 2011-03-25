'''
Written by: loganfynne
'''
from email.parser import HeaderParser
import imaplib, smtplib, email
#import twitter
import facebook
import re

imapmail = ''
smtpmail = ''
user = ''

class Addaccount:
	global imapmail
	global smtpmail
	global user
	def gmail(self):
		global imapmail
		global smtpmail
		global user
		user = raw_input('What is your email username: ')
		password = raw_input('What is your email password: ')

		imapmail = imaplib.IMAP4_SSL('imap.gmail.com', 993) #Connects to Gmail.
		auth, logged = imapmail.login(user, password) #Logs in to Gmail.
		print auth, logged #Outputs success or failure of login.

		smtpmail = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		auth, logged = smtpmail.login(user, password)
		print auth, logged #Outputs success or failure of login.

	def facebook(self):
		fbapi_key = '967f7407da4bc19095c5bcc94b5375ac'
		fbsecret_key = '84a11f3e972a9c94034af84a3b87cfe0'

		Facebook = facebook.Facebook(fbapi_key, fbsecret_key)

		Facebook.auth.createToken()

		# Show login window
		# Set popup=True if you want login without navigational elements
		Facebook.login(popup=True)

		# Login to the window, then press enter
		print 'After logging in, press enter...'
		raw_input()
		Facebook.auth.getSession()
		Facebook.request_extended_permission('read_stream')
		Facebook.request_extended_permission('publish_stream')
		print 'After logging in, press enter...'
		raw_input()
		print 'Login successful.'
		print 'Session Key:   ', Facebook.session_key
		print 'Your UID:      ', Facebook.uid
	def twitter():
		pass


class Epistle:
	def readmail(self):
		global imapmail
		global smtpmail
		global user
		selectlabel = imapmail.select('Inbox')
		print 'Inbox: ', selectlabel[1]
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
				# multipart are just containers, so we skip them
		
				if mailpart.get_content_maintype() == 'multipart':
					continue

				# we are interested only in the simple text messages
				if mailpart.get_content_subtype() != 'plain':
					continue

				payload = mailpart.get_payload()
		  		print payload
	
	def sendmail(self):
		global imapmail
		global smtpmail
		global user
		choice = raw_input('Send email message(1)? ')
		if choice == "1":
			to = raw_input('To: ')
			subject = raw_input('Subject: ')
			mailmessage = raw_input('Message: ')
			smtpmail.sendmail(user,to,'Subject: '+subject+'\n'+mailmessage)

	def updatetwitter(self):
		pass

	def posttwitter(self):
		pass

	def updatefb(self):
		Facebook.stream.get()

	def postfb(self):
		fbstatus = raw_input("Set your Facebook status: ")
		Facebook.status.set(fbstatus)

	def main(self):
		global imapmail
		global smtpmail
		global user
		choose = raw_input ('Do you want to (1)access your mail or (2)post to Facebook: ')
		if choose == "1":
			choice = raw_input('Do you want to (1)read mail or (2)send mail: ')
			if choice == "1": Epistle().readmail()
			elif choice == "2": Epistle().sendmail()

		elif choose == "2":
			choice = raw_input('Do you want to (1)read updates or (2)post updates')
			if choice == "1": Epistle().updatefb()
			elif choice == "2": Epistle().postfb()


Addaccount().gmail()
#Addaccount().facebook()
Epistle().main()
imapmail.logout()
smtpmail.quit()
