from email.parser import HeaderParser
import facebooksdk
import sqlite3
import gobject
import getpass
import imaplib
import smtplib
import tweepy
import webkit
import email
import gtk
import sys
import os

class Database:
	''' Checks for existing database and if one does not exist creates the database. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)

	def check(self):
		if sys.platform == 'linux2':
			self.path = '/home/' + os.environ['USER'] + '/.local/share/epistle.db'

		elif sys.platform == 'win32':
			self.path = 'C:/Users/' + os.getenv('USERNAME') + '/AppData/Local/epistle.db'

		elif sys.platform == 'darwin':
			self.path = '/Users/' + os.getenv('USERNAME') + '/epistle.db'

		self.checkdb = os.path.exists(self.path)
		self.db = sqlite3.connect(self.path)
		self.database = self.db.cursor()
		if self.checkdb == False:
			self.Gmail = Account().gmail()
			self.Twitter = Account().twitter()
			#self.Facebook = Account().facebook()
			self.setup()
		self.Auth,self.Mail = self.read()
		return self.path,self.Auth,self.Mail

	def read(self):
		self.database.execute('select * from auth')
		self.Auth = self.database.fetchall()
		
		self.database.execute('select * from mail where id in (select max(id))')
		self.Mail = self.database.fetchall()
		return self.Auth, self.Mail

	def setup(self):
		try: self.Gmail['gmailuser']
		except NameError: self.Gmail['gmailuser'] = 0
		try: self.Gmail['password']
		except NameError: self.Gmail['password'] = 0
		try: self.Twitter.access_token
		except NameError: self.Twitter.access_token.key,self.Twitter.access_token.secret = 0,0
		self.database.execute('''create table auth (id integer primary key, main)''')
		self.database.execute('insert into auth (id, main) values (1,1)')
		self.database.execute('insert into auth (id, main) values (2,?)', [self.Gmail['gmailuser']])
		self.database.execute('insert into auth (id, main) values (3,?)', [self.Gmail['password']])
		self.database.execute('insert into auth (id, main) values (4,?)', [self.Twitter.access_token.key])
		self.database.execute('insert into auth (id, main) values (5,?)', [self.Twitter.access_token.secret])
		#self.database.execute('insert into auth (main) values (6,?)', [self.Facebook])
		
		self.database.execute('''create table mail (id integer primary key,fromaddress,subject,toaddress,body)''')
		self.database.execute('insert into mail (id,fromaddress,subject,toaddress,body) values (1,"","","","")')
		self.db.commit()
		self.db.close()


class Account:
	''' This function is responsible for adding and removing account information used in Epistle. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)

	def gmail(self):
		''' Collect data for Gmail.'''
		gmailuser = raw_input('What is your email username? ')
		password = getpass.getpass('What is your email password? ')
		returned = {'gmailuser':gmailuser, 'password':password}
		return returned

	def twitter(self):
		''' Collect data for Twitter.'''
		auth = tweepy.OAuthHandler('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
		auth.set_request_token('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
		auth_url = auth.get_authorization_url()
		print 'Please authorize: ', auth_url
		pin = raw_input('PIN: ')
		auth.get_access_token(pin)
		return auth

	def facebook(self):
		'''Collect data for Facebook.'''
		pass

class Epistle:
	''' This is the main application class. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)
		self.path,self.Auth,self.Mail = Database().check()
		
		gobject.threads_init()
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_resizable(False)
		window.set_title('Epistle')
		window.set_size_request(800, 450)
		gtk.window_set_default_icon_from_file('/home/logan/epistle/Epistle-Icon.png')
		window.connect('delete_event', self.delete_event)
		window.connect('destroy', self.destroy)
		window.set_border_width(0)

		toolbar = gtk.Toolbar()
		compose = gtk.Button('Compose')
		compose.connect('clicked', self.showcompose)
		toolbar.add(compose)
		
		if self.Auth[1][0] != int:
			self.logingmail()
			gmail_tab = gtk.Button('Gmail')
			gmail_tab.connect('clicked', self.showmail)
			toolbar.add(gmail_tab)

		if self.Auth[3][0] != int:
			self.logintwitter()
			tweet_tab = gtk.Button('Twitter')
			tweet_tab.connect('clicked', self.showtwitter)
			toolbar.add(tweet_tab)

#		if self.Auth[5][0] != int:
			#self.logingmail()
#			fb_tab = gtk.Button('Facebook')
#			fb_tab.connect('clicked', self.showfb)
#			toolbar.add(fb_tab)
		
		image = gtk.Image()
		image.set_from_stock(gtk.STOCK_REFRESH,gtk.ICON_SIZE_BUTTON)
		refresh_button = gtk.Button()
		refresh_button.set_image(image)
		refresh_button.set_label('')
		refresh_button.connect('clicked', self.refresh)
		toolbar.add(refresh_button)

		#toolbar.insert_space(200)
		#self.search = gtk.Entry()
		#self.search.connect("activate", self.searchdb)
		toolbar.set_size_request(700,35)

		self.html = webkit.WebView()

		self.scrollmsg = gtk.ScrolledWindow(None, None)
		self.scrollmsg.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.scrollmsg.set_size_request(400,415)

		scroll_window = gtk.ScrolledWindow(None, None)
		scroll_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scroll_window.set_size_request(400,415)
		scroll_window.add(self.html)
		
		vbox = gtk.VBox()
		hpane = gtk.HPaned()
		hpane.pack1(self.scrollmsg)
		hpane.pack2(scroll_window)
		#vbox.pack_start(hpane, True, True)
		vbox.add(toolbar)
		vbox.add(hpane)
		window.add(vbox)
		window.show_all()
		self.getmail()
		#self.readmail()
		self.updatetwitter()
		self.listmail()
		
	def delete_event(self, widget, data=None):
		self.imap.logout()
		return False
	
	def destroy(self, widget, data=None):
		gtk.main_quit()

	def getmail(self):
		''' This function reads unread messages from Gmail. '''
		label,inbox = self.imap.select()
		inbox = int(inbox[0])
		unread = len(self.imap.search('Inbox', '(UNSEEN)')[1][0].split())
		self.db = sqlite3.connect(self.path)
		self.database = self.db.cursor()
		self.database.execute('select * from auth where id=1')
		for row in self.database:
			save = row[0]
			print save
		for x in xrange(save+1,inbox):
			resp, data = self.imap.fetch(x, '(RFC822)')
			mailitem = email.message_from_string(data[0][1])
			message = HeaderParser().parsestr(data[0][1])
			self.gmailmessage = {}
			self.gmailmessage['From'] = message['From']
			self.gmailmessage['To'] = message['To']
			self.gmailmessage['Subject'] = message['Subject']

			for mailpart in mailitem.walk():
				if mailpart.get_content_maintype() == 'multipart':
					continue
				message = mailpart.get_payload()
				self.gmailmessage['Body'] = message
			self.database.execute('update auth set main = ? where id = 1', [x])
			self.database.execute('insert into mail (id,fromaddress,subject,toaddress,body) values (?,?,?,?,?)', [ x, self.gmailmessage['From'], self.gmailmessage['Subject'], self.gmailmessage['To'], buffer(self.gmailmessage['Body']) ])

	def sendmail(self):
		''' This function sends an email using Gmail. '''
		self.smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		self.smtp.login(self.Auth[0][0], self.Auth[1][0])
		to = raw_input('To: ')
		subject = raw_input('Subject: ')
		mailmessage = raw_input('Message: ')
		self.smtp.sendmail(self.Gmail[0], to, 'Subject: ' + subject + '\n' +mailmessage)
		self.smtp.quit()

	def updatetwitter(self):
		''' This function updates the user's Tweets. '''
		self.twitterupdate = self.Twitter.home_timeline()

	def posttwitter(self):
		''' This function posts a Tweet. '''
		tweet = raw_input('Update Twitter: ')
		if len(tweet) >= 140:
			while (len(tweet) >= 140):
				print('The character limit of 140 was exceeded.')
				tweet = raw_input('Update Twitter: ')
		self.Twitter.update_status(tweet)

	def updatefb(self):
		''' This function updates the Facebook stream. '''
		self.Facebook['Facebook'] = facebooksdk.GraphAPI(self.Facebook['auth'])
		self.Facebook['profile'] = self.Facebook['Facebook'].get_object('me')
		self.Facebook['friends'] = self.Facebook['Facebook'].get_connections('me', 'friends')
		pass

	def postfb(self):
		''' This function posts to Facebook. '''
		self.Facebook['Facebook'] = facebooksdk.GraphAPI(self.Facebook['auth'])
		self.Facebook['profile'] = self.Facebook['Facebook'].get_object('me')
		self.Facebook['friends'] = self.Facebook['Facebook'].get_connections('me', 'friends')
		fbstatus = raw_input('Set your Facebook status: ')
		self.Facebook['Facebook'].put_object('me', 'feed', message=fbstatus)

	def refresh(self, widget):
		self.getmail()
		self.updatetwitter()

	def readmail(self):
		self.Mail[0][0] #From
		self.Mail[1][0] #Subject
		self.Mail[2][0] #To
		self.Mail[3][0] #Body

	def listmail(self):
		model = gtk.ListStore(gobject.TYPE_STRING)
		tree_view = gtk.TreeView(model)
		self.scrollmsg.add_with_viewport(tree_view)
		tree_view.set_headers_visible(False)
		tree_view.show()

		# Add some messages to the window
		for i in xrange(10):
			msg = self.gmailmessage['Subject'] + ' - ' + self.gmailmessage['From']
			iterator = model.append()
			model.set(iterator, 0, msg)

		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn(None, cell, text=0)
		tree_view.append_column(column)

	def showmail(self, widget):
		''' This function displays email messages. '''
		self.gmailmessage['From'] = self.gmailmessage['From'].replace('<', '&lt;')
		self.gmailmessage['From'] = self.gmailmessage['From'].replace('>', '&gt;')
		self.gmailmessage['Body'] = self.gmailmessage['Body'].replace('\n', '<br />')
		self.html.load_html_string('<p>Subject: ' + self.gmailmessage['Subject'] + '</p><p>From: ' + self.gmailmessage['From'] + '</p><hr />' + self.gmailmessage['Body'], 'file:///')

	def showtwitter(self, widget):
		''' This function displays the user's Twitter home timeline. '''
		tweets = ''
		for x in xrange(0, 17):
			tweets = tweets + '<p><img src="' + self.twitterupdate[x].user.profile_image_url + '"></img><b>' + self.twitterupdate[x].user.screen_name + '</b>: ' + self.twitterupdate[x].text + '</p><hr />'
			self.html.load_html_string(tweets, 'file:///')
		
	def showcompose(self, widget):
		pass
		
	def logingmail(self):
		self.imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
		self.imap.login(self.Auth[1][1], self.Auth[2][1])

	def logintwitter(self):
		self.auth = tweepy.OAuthHandler('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
		self.auth.set_request_token('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
		self.auth.set_access_token(self.Auth[3][1], self.Auth[4][1])
		self.Twitter = tweepy.API(self.auth)

	def main(self):
		''' This function will include the interface of Epistle, and all the function calls. '''
		gtk.main()
if __name__ == '__main__':
	app = Epistle()
	app.main()