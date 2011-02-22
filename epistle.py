'''
Written by: loganfynne
'''
from email.parser import HeaderParser
import imaplib, email, re

user = raw_input('What is your username: ')
password = raw_input('What is your password: ')

mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
auth, logged = mail.login(user, password)
print (auth, logged)

count = mail.select('Inbox')
print ('Inbox: ', count[1])
number = count[1]


messages = mail.status('Inbox', '(MESSAGES)')
print (messages)
unread = mail.status('Inbox', '(UNSEEN)')
print (unread)
recent = mail.status('Inbox', '(RECENT)')
print (recent)

for x in range(1,20):
	resp, data = mail.FETCH(x, '(RFC822)')
	msg = HeaderParser().parsestr(data[0][1])
	print '\n\n\nFrom: ', msg['From']
	print 'To: ', msg['To']
	print 'Subject: ', msg['Subject'], '\n\n'
	
	mailitem = email.message_from_string(data[0][1])
 
	for part in mailitem.walk():
		#print 'Content-Type:', part.get_content_type()
		#print 'Main Content:', part.get_content_maintype()
		#print 'Sub Content:', part.get_content_subtype()
		# multipart are just containers, so we skip them
		if part.get_content_maintype() == 'multipart':
			continue
 
  		# we are interested only in the simple text messages
		if part.get_content_subtype() != 'plain':
			continue
 
		payload = part.get_payload()
  		print payload
 

mail.logout()
