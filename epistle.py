'''
Written by: loganfynne
'''
from email.parser import HeaderParser
import imaplib, email, re

user = raw_input('What is your username: ')
password = raw_input('What is your password: ')

mail = imaplib.IMAP4_SSL('imap.gmail.com', 993) #Connects to Gmail.
auth, logged = mail.login(user, password) #Logs in to Gmail.
print (auth, logged) #Outputs success or failure of login.

count = mail.select('Inbox')
print 'Inbox: ', count[1]
numinbox = re.split('', str(count[1]))
numinbox = '0-9'.join(numinbox)
number = len(numinbox)
x = 0
addto = []
while x < number: #Converts number of items in the inbox into an 'int' object.
	if numinbox[x].isdigit(): addto.append(numinbox[x])
	x = x + 1
numinbox = ''.join(addto)
numinbox = int(numinbox)

messages = mail.status('Inbox', '(MESSAGES)')
print (messages)
unread = mail.status('Inbox', '(UNSEEN)')
print (unread)
recent = mail.status('Inbox', '(RECENT)')
print (recent)

for x in range((numinbox - 50),numinbox):
	resp, data = mail.FETCH(x, '(RFC822)')
	msg = HeaderParser().parsestr(data[0][1])
	print '\n\n\nFrom: ', msg['From']
	print 'To: ', msg['To']
	print 'Subject: ', msg['Subject'], '\n\n'
	
	mailitem = email.message_from_string(data[0][1])
 
	for mailpart in mailitem.walk():
		#print 'Content-Type:', part.get_content_type()
		#print 'Main Content:', part.get_content_maintype()
		#print 'Sub Content:', part.get_content_subtype()
		# multipart are just containers, so we skip them
		if mailpart.get_content_maintype() == 'multipart':
			continue
 
  		# we are interested only in the simple text messages
		if mailpart.get_content_subtype() != 'plain':
			continue
 
		payload = mailpart.get_payload()
  		print payload
 

mail.logout()
