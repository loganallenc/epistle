from email.parser import HeaderParser
import facebooksdk, sqlite3, gobject, getpass, imaplib, smtplib, tweepy, webkit, email, gtk, sys, os

def gmail():
	''' Collect data for Gmail.'''
	gmailuser = raw_input('What is your email username? ')
	password = getpass.getpass('What is your email password? ')
	returned = {'gmailuser':gmailuser, 'password':password}
	return returned

def twitter():
	''' Collect data for Twitter.'''
	auth = tweepy.OAuthHandler('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
	auth.set_request_token('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
	auth_url = auth.get_authorization_url()
	print 'Please authorize: ', auth_url
	pin = raw_input('PIN: ')
	auth.get_access_token(pin)
	return auth

def facebook():
	'''Collect data for Facebook.'''
	pass

class Database:
	''' Checks for existing database and if one does not exist creates the database. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)
		if sys.platform == 'linux2':
			self.path = '/home/' + os.environ['USER'] + '/.local/share/epistle.db'
			self.checkdb = os.path.exists(self.path)
			self.db = sqlite3.connect(self.path)
			self.database = self.db.cursor()
		elif sys.platform == 'win32':
			self.path = 'C:/Users/' + os.getenv('USERNAME') + '/AppData/Local/epistle.db'
			self.checkdb = os.path.exists(self.path)
			self.db = sqlite3.connect(self.path)
			self.database = self.db.cursor()
		elif sys.platform == 'darwin':
			self.checkdb = os.path.exists('/Users/' + os.getenv('USERNAME') + '/epistle.db')
			self.db = sqlite3.connect('/Users/' + os.getenv('USERNAME') + '/epistle.db')
			self.database = self.db.cursor()
		if self.checkdb == False:
			self.Gmail = gmail()
			self.Twitter = twitter()
			#self.Facebook = facebook()
			self.setup()

	def read(self):
		self.database.execute('select * from auth')
		self.Auth = self.database.fetchall()
		
		#self.database.execute('select * from mail')
		#self.Mail = self.database.fetchall()
		return self.Auth

	def setup(self):
		self.database.execute('''create table auth (main)''')
		self.database.execute('insert into auth (main) values (?)', [self.Gmail['gmailuser']])
		self.database.execute('insert into auth (main) values (?)', [self.Gmail['password']])
		self.database.execute('insert into auth (main) values (?)', [self.Twitter.access_token.key])
		self.database.execute('insert into auth (main) values (?)', [self.Twitter.access_token.secret])
		#self.database.execute('insert into auth (main) values (?)', [self.Facebook])
		
		self.database.execute('''create table mail (main)''')
		self.db.commit()
		self.db.close()


class Account:
	''' This function is responsible for adding and removing account information used in Epistle. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)

	def gmail(self):
		''' This function logs the user into their Gmail account. '''
		pass
		
	def twitter(self):
		''' This function logs the user into their Twitter account. '''
		pass

	def facebook(self):
		''' This function logs the user into their Facebook account. '''
		pass

class Epistle:
	''' This is the main application class. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)
		self.Auth = Database().read()
		self.logingmail()
		self.logintwitter()
		
		gobject.threads_init()
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_resizable(False)
		window.set_title('Epistle')
		window.set_size_request(700, 450)
		window.connect('delete_event', self.delete_event)
		window.connect('destroy', self.destroy)
		window.set_border_width(0)
		toolbar = gtk.Toolbar()
		
		compose = gtk.Button('Compose')
		compose.connect('clicked', self.showcompose)
		
		gmail_tab = gtk.Button('Gmail')
		gmail_tab.connect('clicked', self.showmail)
		
		tweet_tab = gtk.Button('Twitter')
		tweet_tab.connect('clicked', self.showtwitter)
			
		image = gtk.Image()
		image.set_from_stock(gtk.STOCK_REFRESH,gtk.ICON_SIZE_BUTTON)
		refresh_button = gtk.Button()
		refresh_button.set_image(image)
		refresh_button.set_label('')
		refresh_button.connect('clicked', self.refresh)

		toolbar.add(compose)
		toolbar.add(gmail_tab)
		toolbar.add(tweet_tab)
		#toolbar.insert_space(200)
		toolbar.add(refresh_button)
		toolbar.set_size_request(700,35)
		#self.search = gtk.Entry()
		#self.search.connect("activate", self.searchdb)

		self.html = webkit.WebView()
		scroll_window = gtk.ScrolledWindow(None, None)
		scroll_window.add(self.html)
		
		vbox = gtk.VBox(False, 0)
		hbox = gtk.HBox(False, 0)
		vbox.pack_start(hbox, expand=False, fill=False, padding=0)
		#Edit the interface to how you like it
		hbox.pack_start(toolbar, expand=False, fill=False, padding=0)
		#hbox.pack_start(self.search, expand=True, fill=True, padding=0)
		vbox.add(scroll_window)
		window.add(vbox)
		window.show_all()
		
	def delete_event(self, widget, data=None):
		self.imap.logout()
		return False
	
	def destroy(self, widget, data=None):
		gtk.main_quit()


	def readmail(self):
		''' This function reads unread messages from Gmail. '''
		label,inbox = self.imap.select('Inbox')
		inbox = int(inbox[0])
		unread = len(self.imap.search('Inbox', '(UNSEEN)')[1][0].split())
		
		for x in range(((inbox - unread)),inbox):
			resp, data = self.imap.FETCH(x, '(RFC822)')
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
				break

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
		pass

	def showmail(self, widget):
		''' This function displays email messages. '''
		self.readmail()
		self.gmailmessage['From'] = self.gmailmessage['From'].replace('<', '&lt;')
		self.gmailmessage['From'] = self.gmailmessage['From'].replace('>', '&gt;')
		self.gmailmessage['Body'] = self.gmailmessage['Body'].replace('\n', '<br />')
		self.html.load_html_string('<p>Subject: ' + self.gmailmessage['Subject'] + '</p><p>From: ' + self.gmailmessage['From'] + '</p><hr />' + self.gmailmessage['Body'], 'file:///')

	def showtwitter(self, widget):
		''' This function displays the user's Twitter home timeline. '''
		self.updatetwitter()
		tweets = ''
		for x in range(0, 19):
			tweets = tweets + '<img width="24" height="24" src="' + self.twitterupdate[x].user.profile_image_url + '"></img><p><b>' + self.twitterupdate[x].user.screen_name + '</b>:' + self.twitterupdate[x].text + '</p><hr />'
		self.html.load_html_string(tweets, 'file:///')
		
	def showcompose(self, widget):
		pass
		
	def logingmail(self):
		self.imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
		self.imap.login(self.Auth[0][0], self.Auth[1][0])

	def logintwitter(self):
		self.auth = tweepy.OAuthHandler('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
		self.auth.set_request_token('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
		self.auth.set_access_token(self.Auth[2][0], self.Auth[3][0])
		self.Twitter = tweepy.API(self.auth)

	def main(self):
		''' This function will include the interface of Epistle, and all the function calls. '''
		gtk.main()
if __name__ == '__main__':
	app = Epistle()
	app.main()