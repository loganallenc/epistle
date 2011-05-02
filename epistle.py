#!/usr/bin/env python2
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
import glib
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
		self.db.text_factory = str
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
		self.database.execute('select * from mail order by id')
		self.Mail = self.database.fetchall()
		return self.Mail

	def setup(self):
		try: self.Gmail['gmailuser']
		except NameError: self.Gmail['gmailuser'] = None
		try: self.Gmail['password']
		except NameError: self.Gmail['password'] = None
		try: self.Twitter.access_token
		except NameError: self.Twitter.access_token.key,self.Twitter.access_token.secret = None,None
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
		glib.threads_init()
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_resizable(False)
		window.set_title('Epistle')
		window.set_size_request(800, 450)
		gtk.window_set_default_icon_from_file('Epistle-Icon.png')
		window.connect('delete_event', self.delete_event)
		window.connect('destroy', self.destroy)
		window.set_border_width(0)

		self.html = webkit.WebView()
		#self.html.connect('load_committed', self.facebook)

		scroll_window = gtk.ScrolledWindow(None, None)
		scroll_window.add(self.html)

		vbox = gtk.VBox(False, 0)
		vbox.pack_start(scroll_window, True, True)

		window.add(vbox)
		window.show_all()
		#self.openfb()
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
		print auth_url
		self.html.open(auth_url)
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
		glib.threads_init()
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_resizable(False)
		window.set_title('Epistle')
		window.set_size_request(800, 450)
		screen = window.get_screen()
		print "Width: " + str(screen.get_width()) + ", Height: " + str(screen.get_height())
		gtk.window_set_default_icon_from_file('Epistle-Icon.png')
		window.connect('delete_event', self.delete_event)
		window.connect('destroy', self.destroy)
		window.connect('key-press-event', self.charcount)
		window.set_border_width(0)

		vbox = gtk.VBox()
		self.notebook = gtk.Notebook()
		self.notebook.set_tab_pos(gtk.POS_TOP)
		self.notebook.set_show_tabs(True)

		self.composevbox = gtk.VBox(False, 0)
		composelabel = gtk.Label('Compose')
		gtk.Widget.show(composelabel)

		if self.Auth[1][0] != None:
			self.tohbox = gtk.HBox(False, 0)
			self.composevbox.pack_start(self.tohbox, False, False, 7)
			tolabel = gtk.Label('To: ')
			self.toentry = gtk.Entry()
			self.tohbox.pack_start(tolabel, False, True, 15)
			self.tohbox.pack_start(self.toentry, True, True, 7)

			self.subjecthbox = gtk.HBox(False, 0)
			self.composevbox.pack_start(self.subjecthbox, False, False, 7)
			subjectlabel = gtk.Label('Subject: ')
			self.subjectentry = gtk.Entry()
			self.subjecthbox.pack_start(subjectlabel, False, True, 7)
			self.subjecthbox.pack_start(self.subjectentry, True, True, 7)

		self.bodyhbox = gtk.HBox(False, 0)
		self.view = gtk.TextView()
		self.buffer = gtk.TextBuffer()
		self.view.set_buffer(self.buffer)
		self.view.set_wrap_mode(True)
		self.bodyhbox.pack_start(self.view, True, True, 15)
		self.composevbox.pack_start(self.bodyhbox, True, True, 10)

		self.actionhbox = gtk.HBox(False, 0)
		send = gtk.Button()
		send.connect('clicked', self.send)
		send.set_label(' Send ')
		discard = gtk.Button()
		discard.connect('clicked', self.discard)
		discard.set_label(' Discard ')
		self.actionhbox.pack_start(send, False, True, 5)
		self.actionhbox.pack_start(discard, False, True, 5)
		if self.Auth[3][0] != None:
			self.twimage = gtk.Image()
			twpixbuf = gtk.gdk.pixbuf_new_from_file('Twitter.png')
			twpixbuf = twpixbuf.scale_simple(22, 22, gtk.gdk.INTERP_BILINEAR)
			self.twimage.set_from_pixbuf(twpixbuf)
			self.twcheck = gtk.CheckButton(None)
			self.twcheck.set_active(False)
			self.count = gtk.Label()
			self.count.set_text('0')
			self.twcheck.connect('toggled', self.showhidetw)

			self.actionhbox.pack_end(self.twcheck, False, True, 5)
			self.actionhbox.pack_end(self.twimage, False, True, 0)
		if self.Auth[1][0] != None:
			self.mailimage = gtk.Image()
			mailpixbuf = gtk.gdk.pixbuf_new_from_file('Gmail.png')
			mailpixbuf = mailpixbuf.scale_simple(22, 22, gtk.gdk.INTERP_BILINEAR)
			self.mailimage.set_from_pixbuf(mailpixbuf)
			self.mailcheck = gtk.CheckButton(None)
			self.mailcheck.set_active(True)
			self.mailcheck.connect('toggled', self.showhidemail)
			self.actionhbox.pack_end(self.mailcheck, False, True, 5)
			self.actionhbox.pack_end(self.mailimage, False, True, 0)

		self.composevbox.pack_start(self.actionhbox, False, False, 10)
		self.notebook.append_page(self.composevbox, composelabel)
		
		if self.Auth[1][0] != None:
			self.logingmail()
			self.getmail()
			gmaillabel = gtk.Label('Gmail')
			gmailevent = gtk.EventBox()
			gmailevent.set_events(gtk.gdk.BUTTON_PRESS_MASK)
			gmailevent.set_visible_window(False)
			gmailevent.connect_after('button-press-event', self.listmail)
			gmailevent.add(gmaillabel)
			gtk.Widget.show(gmaillabel)

			self.viewmail = webkit.WebView()

			self.scrollmsg = gtk.ScrolledWindow(None, None)
			self.scrollmsg.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
			self.scrollmsg.set_size_request(400,415)
	
			scroll_window = gtk.ScrolledWindow(None, None)
			scroll_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
			scroll_window.set_size_request(400,415)
			scroll_window.add(self.viewmail)
		
			hpane = gtk.HPaned()
			hpane.pack1(self.scrollmsg)
			hpane.pack2(scroll_window)

			self.model = gtk.ListStore(gobject.TYPE_STRING)
			self.treeview = gtk.TreeView(self.model)
			self.scrollmsg.add_with_viewport(self.treeview)
			self.treeview.set_headers_visible(False)
			self.treeview.connect('cursor-changed', self.showmail)
			self.treeview.show()
			cell = gtk.CellRendererText()
			column = gtk.TreeViewColumn(None, cell, text=0)
			column.set_max_width(388)
			self.treeview.append_column(column)

			self.notebook.append_page(hpane, gmailevent)

		if self.Auth[3][0] != None:
			self.logintwitter()
			self.updatetwitter()
			twlabel = gtk.Label('Twitter')
			twevent = gtk.EventBox()
			twevent.set_events(gtk.gdk.BUTTON_PRESS_MASK)
			twevent.set_visible_window(False)
			twevent.add(twlabel)
			gtk.Widget.show(twlabel)

			self.viewtw = webkit.WebView()
			scrolltw = gtk.ScrolledWindow(None, None)
			scrolltw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
			scrolltw.set_size_request(800,415)
			scrolltw.add(self.viewtw)
			twbox = gtk.VBox()
			twbox.add(scrolltw)

			tweets = ''
			#tweetleft = '<div style="position: relative; float: left; clear: none; overflow: auto; width: 10%;">'
			#tweetright = '<div style="position: relative; float: right; clear: none; overflow: hidden; width: 90%;">'
			#for x in xrange(0, 17):
			#	tweetleft = tweetleft + '<p><img src="' + self.twitterupdate[x].user.profile_image_url + '"></img></p><p></p><hr />'
			#	tweetright = tweetright + '<p><b>' + self.twitterupdate[x].user.screen_name + '</b></p><p>' + self.twitterupdate[x].text + '</p><hr />'
			for x in xrange(0, 17):
				tweets = tweets + '<div style="width: 100%; display: inline-block;"><span style="vertical-align: middle;"><br /><img src="' + self.twitterupdate[x].user.profile_image_url + '"></img></span><span style="float: right; width: 90%;"><p><b>' + self.twitterupdate[x].user.screen_name + '</b></p><p>' + self.twitterupdate[x].text + '</p></span><hr style="width: 100%;" /></div>'
			#tweetleft = tweetleft + '</div>'
			#tweetright = tweetright + '</div>'
			self.viewtw.load_html_string(tweets, 'file:///')
			self.notebook.append_page(twbox, twevent)

#		if self.Auth[5][0] != None:
#			self.loginfb()
#			fb_tab = gtk.Button('Facebook')
#			fb_tab.connect('clicked', self.showfb)
#			toolbar.add(fb_tab)
#			self.sendfb = False

		refreshimage = gtk.Image()
		refreshimage.set_from_stock(gtk.STOCK_REFRESH,gtk.ICON_SIZE_SMALL_TOOLBAR)
		refreshevent = gtk.EventBox()
		refreshevent.set_events(gtk.gdk.BUTTON_PRESS_MASK)
		refreshevent.set_visible_window(False)
		refreshevent.connect_after('button-press-event', self.refresh)
		refreshevent.add(refreshimage)
		gtk.Widget.show(refreshimage)
		refreshbox = gtk.VBox()
		self.notebook.append_page(refreshbox, refreshevent)

		vbox.add(self.notebook)
		window.add(vbox)
		window.show_all()
		
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
			self.save = row[0]
		while self.save < inbox:
			self.save = self.save + 1
			resp, data = self.imap.fetch(self.save, '(RFC822)')
			mailitem = email.message_from_string(data[0][1])
			header = HeaderParser().parsestr(data[0][1])
			
			for mailpart in mailitem.walk():
				if mailpart.get_content_maintype() == 'multipart':
					continue
				message = str(mailpart.get_payload())
			self.database.execute('update auth set main = ? where id = 1', [self.save])

			if header['Subject'] == None: header['Subject'] = '(No Subject)'

			self.database.execute('insert into mail (id,fromaddress,subject,toaddress,body) values (?,?,?,?,?)', [ self.save, header['From'], header['Subject'], header['To'], message ])
			self.db.commit()
		self.Mail = Database().mailread()

	def send(self, widget):
		if self.mailcheck.get_active() == True:
			self.smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			self.smtp.login(self.Auth[1][1], self.Auth[2][1])
			to = self.toentry.get_text()
			subject = self.subjectentry.get_text()
			body = self.buffer.get_text(self.buffer.get_start_iter(),self.buffer.get_end_iter())
			self.smtp.sendmail(self.Auth[2][1], to, 'Subject: ' + subject + '\n' + body)
			self.smtp.quit()
		if self.twcheck.get_active() == True:
			body = self.buffer.get_text(self.buffer.get_start_iter(),self.buffer.get_end_iter())
			self.Twitter.update_status(body)
		self.discard(0)

	def discard(self, widget):
		self.toentry.set_text('')
		self.subjectentry.set_text('')
		self.buffer.set_text('')
		self.charcount(1,1)

	def showhidemail(self, widget):
		if self.mailcheck.get_active() == True:
			self.composevbox.remove(self.bodyhbox)
			self.composevbox.remove(self.actionhbox)
			self.composevbox.pack_start(self.tohbox, False, False, 7)
			self.composevbox.pack_start(self.subjecthbox, False, False, 7)
			self.composevbox.pack_start(self.bodyhbox, True, True, 10)
			self.composevbox.pack_start(self.actionhbox, False, False, 10)
		elif self.mailcheck.get_active() == False:
			self.composevbox.remove(self.tohbox)
			self.composevbox.remove(self.subjecthbox)

	def showhidetw(self, widget):
		if self.twcheck.get_active() == True:
			self.actionhbox.pack_end(self.count, True, True, 0)
			gtk.Widget.show(self.count)
		elif self.twcheck.get_active() == False:
			self.actionhbox.remove(self.count)

	def charcount(self, widget, callback):
		num = self.buffer.get_char_count()
		if num != 0: num = num + 1
		num = 140 - num
		self.count.set_text(str(num))
			
	def updatetwitter(self):
		''' This function updates the user's Tweets. '''
		self.twitterupdate = self.Twitter.home_timeline()

	def updatefb(self):
		''' This function updates the Facebook stream. '''
		self.Facebook['Facebook'] = facebooksdk.GraphAPI(self.Facebook['auth'])
		self.Facebook['profile'] = self.Facebook['Facebook'].get_object('me')
		self.Facebook['friends'] = self.Facebook['Facebook'].get_connections('me', 'friends')

	def postfb(self):
		''' This function posts to Facebook. '''
		self.Facebook['Facebook'] = facebooksdk.GraphAPI(self.Facebook['auth'])
		self.Facebook['profile'] = self.Facebook['Facebook'].get_object('me')
		self.Facebook['friends'] = self.Facebook['Facebook'].get_connections('me', 'friends')
		fbstatus = raw_input('Set your Facebook status: ')
		self.Facebook['Facebook'].put_object('me', 'feed', message=fbstatus)

	def refresh(self, widget, widget2):
		''' Refreshes data. '''
		if self.Auth[1][0] != None: self.getmail()
		if self.Auth[3][0] != None:
			self.updatetwitter()
			tweets = ''
			for x in xrange(0, 17):
				tweets = tweets + '<div><span style="float: left; width: 10%;"><img src="' + self.twitterupdate[x].user.profile_image_url + '"></img></span>'
				tweets = tweets + '<span style="float: right; width: 90%;"><p><b>' + self.twitterupdate[x].user.screen_name + '</b></p><p>' + self.twitterupdate[x].text + '</p><hr /></span></div>'
				self.viewtw.load_html_string(tweets, 'file:///')

	def listmail(self, widget, widget2):
		''' Shows list of mail. '''
		for x in xrange(0,49):
			y = self.save + x - 50
			msg = self.Mail[y][2] + ' - ' + self.Mail[y][1] + ' '*60 + str(x)
			self.iterator = self.model.prepend()
			self.model.set(self.iterator, 0, msg)

	def showmail(self, widget):
		''' This function displays email messages. '''
		selection = self.treeview.get_selection()
		selection.set_mode(gtk.SELECTION_SINGLE)
		model, path = selection.get_selected()
		x = model[path][0]
		last = len(x)
		x = list(x)
		if x[last-2].isdigit():
			x = int(x[last-2] + x[last-1])
		else: x = int(x[last-1])
		y = self.save + x - 50
		self.viewmail.load_html_string(self.Mail[y][4], 'file:///')

	def logingmail(self):
		''' Logs in to Gmail. '''
		self.imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
		self.imap.login(self.Auth[1][1], self.Auth[2][1])

	def logintwitter(self):
		''' Logs into Twitter. '''
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