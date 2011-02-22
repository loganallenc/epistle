'''
Written by: loganfynne
Initial command-line mail function of Epistle. Can't read mail yet, or really do much of anything. Full email support, Twitter support, Facebook support, and a GUI needed.
'''
import imaplib, re
user = raw_input('What is your username: ')
password = raw_input('What is your password: ')

mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
auth, logged = mail.login(user, password)
print (auth, logged)

count = mail.select('Inbox')
print (count[1])

messages = mail.status('Inbox', '(MESSAGES)')
print (messages)
unread = mail.status('Inbox', '(UNSEEN)')
print (unread)
recent = mail.status('Inbox', '(RECENT)')
print (recent)

mail.logout()
