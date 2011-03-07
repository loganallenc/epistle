'''
Written by: loganfynne
'''
from email.parser import HeaderParser
import imaplib, smtplib, email
#import twitter
import facebook
import re

user = raw_input('What is your email username: ')
password = raw_input('What is your email password: ')

imapmail = imaplib.IMAP4_SSL('imap.gmail.com', 993) #Connects to Gmail.
auth, logged = imapmail.login(user, password) #Logs in to Gmail.
print auth, logged #Outputs success or failure of login.
smtpmail = smtplib.SMTP_SSL('smtp.gmail.com', 465)
auth, logged = smtpmail.login(user, password)
print auth, logged #Outputs success or failure of login.

api_key = ''
secret_key = ''

Facebook = facebook.Facebook(api_key, secret_key)

Facebook.auth.createToken()

# Show login window
# Set popup=True if you want login without navigational elements
Facebook.login()

# Login to the window, then press enter
print 'After logging in, press enter...'
raw_input()

Facebook.auth.getSession()
print 'Session Key:   ', Facebook.session_key
print 'Your UID:      ', Facebook.uid


class Epistle:
	def __init__(self):
		from email.parser import HeaderParser
		import imaplib, smtplib, email, re, twitter

	def readmail(self):
		global imapmail
		global smtpmail
		global user
		selectlabel = imapmail.select('Inbox')
		print 'Inbox: ', selectlabel[1]
		numinbox = re.split('', str(selectlabel[1]))
		numinbox = '0-9'.join(numinbox)
		number = len(numinbox)
		x = 0
		addto = []
		while x < number: #Converts number of items in the inbox into an 'int' object.
			if numinbox[x].isdigit(): addto.append(numinbox[x])
			x = x + 1
		numinbox = ''.join(addto)
		numinbox = int(numinbox)

		messages = imapmail.status('Inbox', '(MESSAGES)')
		print 'Total: ', messages
		unread = imapmail.status('Inbox', '(UNSEEN)')
		print 'Unread: ', unread
		recent = imapmail.status('Inbox', '(RECENT)')
		print 'Recent: ', recent
		#status, email_ids = imapmail.search(None, '(UNSEEN)')
		#print email_ids

		for x in range((numinbox - 15),numinbox):
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
		elif choice == "2":
			fbstatus = raw_input("Set your Facebook status: ")
			facebook.status.set(fbstatus)

		
	def main(self):
		global imapmail
		global smtpmail
		global user
		choose = raw_input ('Do you want to read your most recent mail(1), or write a message(2)? ')
		if choose == "1":
			Epistle().readmail()
		if choose == "2":
			Epistle().sendmail()

Epistle().main()
imapmail.logout()
smtpmail.quit()
