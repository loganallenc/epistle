'''
Written by: loganfynne
'''
from email.parser import HeaderParser
import imaplib, smtplib, email, re

user = raw_input('What is your username: ')
password = raw_input('What is your password: ')

imapmail = imaplib.IMAP4_SSL('imap.gmail.com', 993) #Connects to Gmail.
auth, logged = imapmail.login(user, password) #Logs in to Gmail.
print (auth, logged) #Outputs success or failure of login.
smtpmail = smtplib.SMTP_SSL('smtp.gmail.com', 465)
auth, logged = smtpmail.login(user, password)
print (auth, logged) #Outputs success or failure of login.

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
status, email_ids = imapmail.search(None, '(UNSEEN)')
print email_ids

for x in range((numinbox - 50),numinbox):
	resp, data = imapmail.FETCH(x, '(RFC822)')
	msg = HeaderParser().parsestr(data[0][1])
	print '\n\n\nFrom: ', msg['From']
	print 'To: ', msg['To']
	print 'Subject: ', msg['Subject'], '\n\n'
	
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

imapmail.logout()
smtpmail.quit()
