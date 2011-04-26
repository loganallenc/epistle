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
		if sys.platform == 'linux2':
			self.path = '/home/' + os.environ['USER'] + '/.local/share/epistle.db'
		if sys.platform == 'win32':
			self.path = 'C:/Users/' + os.getenv('USERNAME') + '/AppData/Local/epistle.db'
		elif sys.platform == 'darwin':
			self.path = '/Users/' + os.getenv('USERNAME') + '/epistle.db'

	def connect(self):
		self.checkdb = os.path.exists(self.path)
		self.db = sqlite3.connect(self.path)
		self.database = self.db.cursor()
		return self.db, self.database
	
	def check(self):
		self.connect()
		if self.checkdb == False:
			self.Gmail = Account().gmail()
			self.Twitter = Account().twitter()
			#self.Facebook = Account().facebook()
			self.setup()
		self.Auth = self.authread()
		return self.path,self.Auth

	def authread(self):
		self.connect()
		self.database.execute('select * from auth')
		self.Auth = self.database.fetchall()
		return self.Auth

	def mailread(self):
		self.connect()
		self.database.execute('select * from mail where id in (select max(id))')
		self.Mail = self.database.fetchall()
		return self.Mail

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
		
		self.database.execute('''create table mail (id primary key,fromaddress,subject,toaddress,body)''')
		self.db.commit()


class Account:
	''' This function is responsible for adding and removing account information used in Epistle. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_resizable(False)
		self.window.set_title("Epistle")
		self.window.set_default_size(800, 450)
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)

		self.html = webkit.WebView()
		self.html.connect('load_committed', self.facebook)

		scroll_window = gtk.ScrolledWindow(None, None)
		scroll_window.add(self.html)

		vbox = gtk.VBox(False, 0)
		vbox.pack_start(scroll_window, True, True)

		self.window.add(vbox)
		self.window.show_all()
		self.openfb()
		gtk.main()

	def delete_event(self, widget, data=None):
		return False
	
	def destroy(self, widget, data=None):
		gtk.main_quit()

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

	def openfb(self):
		self.html.open('https://www.facebook.com/dialog/oauth?client_id=198204650217009&redirect_uri=http://www.loganfynne.com/')
	def facebook(self,widget,data=None):
		'''Collect data for Facebook.'''
		url = widget.get_main_frame().get_uri()
		url = url.replace ('http://www.loganfynne.com/?code=','')
		url = url.split('.', 1)
		url = url.pop()
		url = ''.join(url)
		print url

class Epistle:
	''' This is the main application class. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)
		self.path,self.Auth = Database().check()
		
		gobject.threads_init()
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_resizable(False)
		window.set_title('Epistle')
		window.set_size_request(800, 450)
		gtk.window_set_default_icon_from_file('Epistle-Icon.png')
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
			#self.loginfb()
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
		self.gtkbuffer = gtk.TextBuffer()
		self.view = gtk.TextView()

		self.scrollmsg = gtk.ScrolledWindow(None, None)
		self.scrollmsg.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.scrollmsg.set_size_request(400,415)

		scroll_window = gtk.ScrolledWindow(None, None)
		scroll_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scroll_window.set_size_request(400,415)
		scroll_window.add(self.view)
		
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
		self.updatetwitter()
		self.listmail()
		
	def delete_event(self, widget, data=None):
		self.imap.logout()
		self.db.close()
		return False
	
	def destroy(self, widget, data=None):
		gtk.main_quit()

	def getmail(self):
		''' This function reads unread messages from Gmail. '''
		label,inbox = self.imap.select()
		inbox = int(inbox[0])
		unread = len(self.imap.search('Inbox', '(UNSEEN)')[1][0].split())
		self.db,self.database = Database().connect()
		self.database.execute('select main from auth where id=1')
		for row in self.database:
			save = row[0]
			print 'Num in DB: ' + str(save)
			print 'Inbox: ' + str(inbox)
		while save < inbox:
			save = save + 1
			print save
			resp, data = self.imap.fetch(save, '(RFC822)')
			mailitem = email.message_from_string(data[0][1])
			header = HeaderParser().parsestr(data[0][1])

			for mailpart in mailitem.walk():
				if mailpart.get_content_maintype() == 'multipart':
					continue
				if mailpart.get_payload() == str: message = mailpart.get_payload()
				else: message = '' 
			self.database.execute('update auth set main = ? where id = 1', [save])
			self.database.execute('insert into mail (id,fromaddress,subject,toaddress,body) values (?,?,?,?,?)', [ save, header['From'], header['Subject'], header['To'], message ])
			self.db.commit()

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
		self.Mail = Database().mailread()

	def listmail(self):
		self.readmail()
		self.model = gtk.ListStore(gobject.TYPE_STRING)
		treeview = gtk.TreeView(self.model)
		self.scrollmsg.add_with_viewport(treeview)
		treeview.set_headers_visible(False)
		treeview.show()

		# Add some messages to the window
		for x in xrange(0,19):
			print 'Listed Email: ' + str(x)
			msg = self.Mail[x][2] + ' - ' + self.Mail[x][1]
			self.iterator = self.model.append()
			self.model.set(self.iterator, 0, msg)

		cell = gtk.CellRendererText()
		column = gtk.TreeViewColumn(None, cell, text=0)
		treeview.append_column(column)

	def showmail(self, widget):
		''' This function displays email messages. '''
		self.model.get_value(self.iterator, 0)
		self.gtkbuffer.set_text(self.Mail[0][4])
		self.view.set_buffer(gtkbuffer)

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
	#app = Epistle()
	#app.main()
	Account()
