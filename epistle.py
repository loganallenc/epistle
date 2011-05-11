#!/usr/bin/env python2
from email.parser import HeaderParser
from threading import Thread
import facebooksdk
import sqlite3
import getpass
import imaplib
import smtplib
import tweepy
import urllib
import webkit
import email
import gobject
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
		self.folder = self.path
		self.folder = self.folder.replace('.db','')
		if os.path.exists(self.folder) == False:
			os.makedirs(self.folder)

	def connect(self):
		self.checkdb = os.path.exists(self.path)
		self.db = sqlite3.connect(self.path)
		self.database = self.db.cursor()
		self.db.text_factory = str
		return self.db, self.database

	def check(self):
		self.connect()
		if self.checkdb == False:
			self.gmailusername,self.gmailpassword,self.twoauth,self.twcheck,self.fboauth = Account().finish(0)
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
		self.database.execute('''create table auth (id integer primary key, main)''')
		self.database.execute('insert into auth (id, main) values (1,1)')
		self.database.execute('insert into auth (id, main) values (2,?)', [self.gmailusername])
		self.database.execute('insert into auth (id, main) values (3,?)', [self.gmailpassword])
		if self.twcheck.get_active() == False:
			self.database.execute('insert into auth (id, main) values (4,?)', [None])
			self.database.execute('insert into auth (id, main) values (5,?)', [None])
		elif self.twcheck.get_active() == True:
			self.database.execute('insert into auth (id, main) values (4,?)', [self.twoauth.access_token.key])
			self.database.execute('insert into auth (id, main) values (5,?)', [self.twoauth.access_token.secret])
		self.database.execute('insert into auth (id, main) values (6,?)', [self.fboauth])
		self.database.execute('''create table mail (id primary key,fromaddress,subject,toaddress,body)''')
		self.db.commit()


class Account:
	''' This function is responsible for adding and removing account information used in Epistle. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)
		gtk.gdk.threads_init()
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_resizable(False)
		self.window.set_title('Epistle')
		self.window.set_size_request(800, 500)
		gtk.window_set_default_icon_from_file('/usr/share/epistle/Icon.png')
		self.window.connect('delete_event', self.delete_event)
		self.window.connect('destroy', self.destroy)
		self.window.set_border_width(0)

		self.html = webkit.WebView()
		self.html.connect('load_committed', self.facebook)

		self.scroll_window = gtk.ScrolledWindow(None, None)
		self.scroll_window.add(self.html)

		self.vbox = gtk.VBox(False, 0)

		firstcontainer = gtk.HBox(False, 0)
		label = gtk.Label('Epistle Account Setup')
		separator = gtk.HSeparator()
		firstcontainer.pack_start(label, False, False, 10)
		self.vbox.pack_start(firstcontainer, False, False, 10)
		self.vbox.pack_start(separator, False, False, 20)

		containermail = gtk.HBox(False, 0)
		selecthboxmail = gtk.HBox(False, 0)
		self.mailimage = gtk.Image()
		mailpixbuf = gtk.gdk.pixbuf_new_from_file('/usr/share/epistle/Gmail.png')
		mailpixbuf = mailpixbuf.scale_simple(48, 48, gtk.gdk.INTERP_BILINEAR)
		self.mailimage.set_from_pixbuf(mailpixbuf)
		self.mailcheck = gtk.CheckButton(None)
		self.mailcheck.set_active(True)
		maillabel = gtk.Label('Gmail')
		selecthboxmail.pack_start(maillabel, False, True, 19)
		selecthboxmail.pack_start(self.mailcheck, False, True, 15)
		selecthboxmail.pack_start(self.mailimage, False, True, 4)
		containermail.pack_start(selecthboxmail, True, False, 100)
		self.vbox.pack_start(containermail, False, False, 20)

		containertw = gtk.HBox(False, 0)
		selecthboxtw = gtk.HBox(False, 0)
		self.twimage = gtk.Image()
		twpixbuf = gtk.gdk.pixbuf_new_from_file('/usr/share/epistle/Twitter.png')
		twpixbuf = twpixbuf.scale_simple(40, 40, gtk.gdk.INTERP_BILINEAR)
		self.twimage.set_from_pixbuf(twpixbuf)
		self.twcheck = gtk.CheckButton(None)
		self.twcheck.set_active(True)
		twlabel = gtk.Label('Twitter')
		selecthboxtw.pack_start(twlabel, False, True, 18)
		selecthboxtw.pack_start(self.twcheck, False, True, 14)
		selecthboxtw.pack_start(self.twimage, False, True, 8)
		containertw.pack_start(selecthboxtw, True, False, 100)
		self.vbox.pack_start(containertw, False, False, 20)
		
		containerfb = gtk.HBox(False, 0)
		selecthboxfb = gtk.HBox(False, 0)
		self.fbimage = gtk.Image()
		fbpixbuf = gtk.gdk.pixbuf_new_from_file('/usr/share/epistle/Facebook.png')
		fbpixbuf = fbpixbuf.scale_simple(36, 36, gtk.gdk.INTERP_BILINEAR)
		self.fbimage.set_from_pixbuf(fbpixbuf)
		self.fbcheck = gtk.CheckButton(None)
		self.fbcheck.set_active(True)
		fblabel = gtk.Label('Facebook')
		selecthboxfb.pack_start(fblabel, False, True, 10)
		selecthboxfb.pack_start(self.fbcheck, False, True, 10)
		selecthboxfb.pack_start(self.fbimage, False, True, 10)
		containerfb.pack_start(selecthboxfb, True, False, 100)
		self.vbox.pack_start(containerfb, False, False, 20)
		
		placebutton_one = gtk.HBox(False, 0)
		forward_one = gtk.Button('Continue')
		forward_one.connect('clicked', self.forward)
		self.pagenum = 0
		placebutton_one.pack_end(forward_one, False, True, 10)
		self.vbox.pack_end(placebutton_one, False, False, 10)

		self.gmailwindow = gtk.VBox(False, 0)
		self.userhbox = gtk.HBox(False, 0)
		userlabel = gtk.Label(' Username: ')
		self.userentry = gtk.Entry()
		self.passhbox = gtk.HBox(False, 0)
		passlabel = gtk.Label(' Password: ')
		self.passentry = gtk.Entry()
		self.passentry.set_visibility(gtk.FALSE)
		self.confhbox = gtk.HBox(False, 0)
		conflabel = gtk.Label(' Confirm: ')
		self.confentry = gtk.Entry()
		self.confentry.set_visibility(gtk.FALSE)
		self.userhbox.pack_start(userlabel, False, True, 15)
		self.userhbox.pack_start(self.userentry, True, True, 7)
		self.passhbox.pack_start(passlabel, False, True, 15)
		self.passhbox.pack_start(self.passentry, True, True, 7)
		self.confhbox.pack_start(conflabel, False, True, 15)
		self.confhbox.pack_start(self.confentry, True, True, 7)
		self.gmailwindow.add(self.userhbox)
		self.gmailwindow.add(self.passhbox)
		self.gmailwindow.add(self.confhbox)
		
		self.placebutton_two = gtk.HBox(False, 0)
		forward_two = gtk.Button('Continue')
		forward_two.connect('clicked', self.forward)
		back_two = gtk.Button('Back')
		back_two.connect('clicked', self.back)
		self.placebutton_two.pack_start(back_two, False, True, 10)
		self.placebutton_two.pack_end(forward_two, False, True, 10)
		self.passchecklabel = gtk.Label('Passwords do not match')
		self.gmailwindow.pack_end(self.placebutton_two, False, False, 10)

		self.twwindow = gtk.VBox(False, 0)
		self.twhpane = gtk.HPaned()
		twhbox = gtk.HBox(False, 0)
		twitterlabel = gtk.Label('Twitter PIN: ')
		self.twentry = gtk.Entry()
		twhbox.pack_start(twitterlabel, False, True, 15)
		twhbox.pack_start(self.twentry, True, True, 15)
		self.twhpane.pack1(twhbox)
		self.twhpane.pack2(self.scroll_window)
		self.twwindow.add(self.twhpane)
		self.twchecklabel = gtk.Label('You have to enter in the PIN.')
		
		self.placebutton_three = gtk.HBox(False, 0)
		forward_three = gtk.Button('Continue')
		forward_three.connect('clicked', self.forward)
		back_three = gtk.Button('Back')
		back_three.connect('clicked', self.back)
		self.placebutton_three.pack_start(back_three, False, True, 10)
		self.placebutton_three.pack_end(forward_three, False, True, 10)
		self.twwindow.pack_end(self.placebutton_three, False, False, 10)

		self.fbwindow = gtk.VBox(False, 0)
		self.fbpage = gtk.VBox(False, 0)
		
		self.placebutton_four = gtk.HBox(False, 0)
		forward_four = gtk.Button('Continue')
		forward_four.connect('clicked', self.forward)
		back_four = gtk.Button('Back')
		back_four.connect('clicked', self.back)
		self.placebutton_four.pack_start(back_four, False, True, 10)
		self.placebutton_four.pack_end(forward_four, False, True, 10)
		self.fbwindow.pack_end(self.placebutton_four, False, False, 10)
		
		self.finishwindow = gtk.VBox(False, 0)
		finishlabel = gtk.Label('Thank you for setting up your accounts.\nYou may now close this window.')
		self.finishwindow.add(finishlabel)
		
		self.wait = False
		self.window.add(self.vbox)
		self.window.show_all()
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
		try:
			pin = self.twentry.get_text()
			self.twoauth.get_access_token(pin)
		except tweepy.error.TweepError:
			self.twoauth.set_access_token(None,None)
		
	def facebook(self,widget,data=None):
		''' Collect data for Facebook. '''
		if 'http://www.loganfynne.com/' in widget.get_main_frame().get_uri():
			import urlparse
			self.fboauth = widget.get_main_frame().get_uri()
			self.fboauth = self.fboauth.replace('http://www.loganfynne.com/#access_token=','')
			self.fboauth = self.fboauth.replace('&expires_in=0','')
			print self.fboauth

	def back(self, widget):
		''' Go the previous page. '''
		if self.pagenum == 1:
			self.pagenum = 0
			self.window.remove(self.gmailwindow)
			self.window.add(self.vbox)
		elif self.pagenum == 2:
			self.pagenum = 1
			self.window.remove(self.twwindow)
			if self.mailcheck.get_active() == True:
				self.window.add(self.gmailwindow)
			else:
				self.window.add(self.vbox)
		elif self.pagenum == 3:
			self.pagenum = 2
			self.window.remove(self.fbwindow)
			if self.twcheck.get_active() == True:
				self.fbwindow.remove(self.scroll_window)
				self.twhpane.pack2(self.scroll_window)
				auth_url = self.twoauth.get_authorization_url()
				self.html.open(auth_url)
				self.window.add(self.twwindow)
			else:
				if self.mailcheck.get_active() == True:
					self.window.add(self.mailwindow)
				else:
					self.window.add(self.vbox)
	def forward(self, widget):
		''' Go to the next page. '''
		if self.wait == True: 
			self.wait = False
		else:
			if self.pagenum == 0:
				self.window.remove(self.vbox)
				if self.mailcheck.get_active() == True:
					self.window.add(self.gmailwindow)
					self.wait = True	
				self.pagenum = 1
		if self.wait == False:
			if self.pagenum == 1:
				if self.mailcheck.get_active() == True:
					if self.passentry.get_text() == self.confentry.get_text():
						self.window.remove(self.gmailwindow)
						self.gmailusername = self.userentry.get_text()
						self.gmailpassword = self.passentry.get_text()
						self.twoauth = tweepy.OAuthHandler('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
						auth_url = self.twoauth.get_authorization_url()
						if self.twcheck.get_active() == True:
							self.html.open(auth_url)
							self.window.add(self.twwindow)
							self.wait = True
						self.pagenum = 2
					else:
						self.gmailwindow.remove(self.placebutton_two)
						self.gmailwindow.pack_end(self.passchecklabel, False, False, 10)
						self.gmailwindow.pack_end(self.placebutton_two, False, False, 10)
				else:
					self.twoauth = tweepy.OAuthHandler('yE6isPwi45JwhEnHMphdcQ', '90JOy6EL74Y9tdkG7ya9P7XpwCpOUbATYWZvoYiuCw')
					auth_url = self.twoauth.get_authorization_url()
					if self.twcheck.get_active() == True:
						self.html.open(auth_url)
						self.window.add(self.twwindow)
						self.wait = True
					self.pagenum = 2
					self.gmailusername = None
					self.gmailpassword = None
		if self.wait == False:
			if self.pagenum == 2:
				if self.twcheck.get_active() == True:
					if self.twentry.get_text() == '':
						self.twwindow.remove(self.placebutton_three)
						self.twwindow.pack_end(self.twchecklabel, False, False, 10)
						self.twwindow.pack_end(self.placebutton_three, False, False, 10)
					else:
						self.window.remove(self.twwindow)
						self.twitter()
						self.pagenum = 3
						if self.fbcheck.get_active() == True:
							self.wait = True
							self.twhpane.remove(self.scroll_window)
							self.fbwindow.add(self.scroll_window)
							self.html.close()
							self.html.connect_after('load_committed', self.facebook)
							self.html.open('https://graph.facebook.com/oauth/authorize?type=user_agent&client_id=198204650217009&scope=read_stream,publish_stream,offline_access&redirect_uri=http://www.loganfynne.com/')
							self.window.add(self.fbwindow)
							self.pagenum = 3
				else:
					if self.fbcheck.get_active() == True:
							self.wait = True
							self.twhpane.remove(self.scroll_window)
							self.fbwindow.add(self.scroll_window)
							self.html.close()
							self.html.connect_after('load_committed', self.facebook)
							self.html.open('https://graph.facebook.com/oauth/authorize?type=user_agent&client_id=198204650217009&scope=read_stream,publish_stream,offline_access&redirect_uri=http://www.loganfynne.com/')
							self.window.add(self.fbwindow)
					self.twoauth = None
					self.pagenum = 3
		if self.wait == False:
			if self.pagenum == 3:
				if self.fbcheck.get_active() == True:
					self.window.remove(self.fbwindow)
				else:
					if self.twcheck.get_active() == False:
						if self.mailcheck.get_active() == False:
							self.pagenum = 0
					self.fboauth = None
				if self.pagenum == 0:
					self.window.remove(self.finishwindow)
					self.window.add(self.vbox)
				self.window.add(self.finishwindow)
		self.window.show_all()
		
	def finish(self, widget):
		return self.gmailusername,self.gmailpassword,self.twoauth,self.twcheck,self.fboauth


class Epistle:
	''' This is the main application class. '''
	def __init__(self, *args, **kwargs):
		self.__dict__.update(kwargs)
		self.path,self.Auth = Database().check()
		gtk.gdk.threads_init()
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_resizable(True)
		window.set_title('Epistle')
		window.set_size_request(800, 450)
		gtk.window_set_default_icon_from_file('/usr/share/epistle/Icon.png')
		window.connect('destroy', self.destroy)
		window.connect('key-press-event', self.charcount)
		window.set_border_width(0)

		vbox = gtk.VBox()
		self.notebook = gtk.Notebook()
		self.notebook.set_tab_pos(gtk.POS_TOP)
		self.notebook.set_show_tabs(True)

		self.count = gtk.Label()
		self.count.set_text('0')

		self.composevbox = gtk.VBox(False, 0)
		composelabel = gtk.Label('Compose')
		gtk.Widget.show(composelabel)

		if self.Auth[1][1] != None:
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
		
		self.mailcheck = gtk.CheckButton(None)

		self.twcheck = gtk.CheckButton(None)
		self.twcheck.set_active(False)
		self.fbcheck = gtk.CheckButton(None)
		self.fbcheck.set_active(False)
		if self.Auth[5][1] != None:
			self.fbimage = gtk.Image()
			fbpixbuf = gtk.gdk.pixbuf_new_from_file('/usr/share/epistle/Facebook.png')
			fbpixbuf = fbpixbuf.scale_simple(22, 22, gtk.gdk.INTERP_BILINEAR)
			self.fbimage.set_from_pixbuf(fbpixbuf)
			self.actionhbox.pack_end(self.fbcheck, False, True, 5)
			self.actionhbox.pack_end(self.fbimage, False, True, 0)
		if self.Auth[3][1] != None:
			self.twimage = gtk.Image()
			twpixbuf = gtk.gdk.pixbuf_new_from_file('/usr/share/epistle/Twitter.png')
			twpixbuf = twpixbuf.scale_simple(22, 22, gtk.gdk.INTERP_BILINEAR)
			self.twimage.set_from_pixbuf(twpixbuf)
			self.twcheck.connect('toggled', self.showhidetw)
			self.actionhbox.pack_end(self.twcheck, False, True, 5)
			self.actionhbox.pack_end(self.twimage, False, True, 0)
		if self.Auth[1][1] != None:
			self.mailimage = gtk.Image()
			mailpixbuf = gtk.gdk.pixbuf_new_from_file('/usr/share/epistle/Gmail.png')
			mailpixbuf = mailpixbuf.scale_simple(22, 22, gtk.gdk.INTERP_BILINEAR)
			self.mailimage.set_from_pixbuf(mailpixbuf)
			self.mailcheck.connect('toggled', self.showhidemail)
			self.mailcheck.set_active(True)
			self.actionhbox.pack_end(self.mailcheck, False, True, 5)
			self.actionhbox.pack_end(self.mailimage, False, True, 0)
		else: self.mailcheck.set_active(False)
		self.composevbox.pack_start(self.actionhbox, False, False, 10)
		self.notebook.append_page(self.composevbox, composelabel)
		
		if self.Auth[1][1] != None:
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

		if self.Auth[3][1] != None:
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
			for x in xrange(0, 17):
				tweets = tweets + '<div style="width: 100%; display: inline-block;"><span style="vertical-align: middle;"><br /><img src="' + self.twitterupdate[x].user.profile_image_url + '"></img></span><span style="float: right; width: 90%;"><p><b>' + self.twitterupdate[x].user.screen_name + '</b></p><p>' + self.twitterupdate[x].text + '</p></span><hr style="width: 100%;" /></div>'
			self.viewtw.load_html_string(tweets, 'file:///')
			self.notebook.append_page(twbox, twevent)

		if self.Auth[5][1] != None:
			self.loginfb()
			fblabel = gtk.Label('Facebook')
			fbevent = gtk.EventBox()
			fbevent.set_events(gtk.gdk.BUTTON_PRESS_MASK)
			fbevent.set_visible_window(False)
			fbevent.add(fblabel)
			gtk.Widget.show(fblabel)
			
			self.viewfb = webkit.WebView()
			scrollfb = gtk.ScrolledWindow(None, None)
			scrollfb.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
			scrollfb.set_size_request(800,415)
			scrollfb.add(self.viewfb)
			fbbox = gtk.VBox()
			fbbox.add(scrollfb)
			fbposts = urllib.urlopen('https://graph.facebook.com/me/home?access_token=' + self.Auth[5][1])
			fbfeed = fbposts.read()
			fbposts.close()
			fbparsed = ''
			fbfeed = fbfeed.split('"',fbfeed.count('"'))
			for x in xrange(0,(len(fbfeed))):
				if fbfeed[x] == 'name':
					if fbfeed[x-2] == 'from': 
						fbparsed = fbparsed + '<p><b>' + fbfeed[x+2] + '</b></p>'
				if fbfeed[x] == 'message':
					fbparsed = fbparsed + '<p>' + fbfeed[x+2] + '</p><hr />'
			self.viewfb.load_html_string(fbparsed, 'file:///')
			self.notebook.append_page(fbbox, fbevent)

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

	def destroy(self, widget, data=None):
		if self.Auth[1][1] != None:
			self.imap.logout()
			self.db.close()
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
				if mailpart.get_filename() != None:
					fp = open(path + '/' + mailpart.get_filename(), 'w')
					fp.write(mailpart.get_payload(decode=True))
					fp.close()
				message = str(mailpart.get_payload(decode=True))
			self.database.execute('update auth set main = ? where id = 1', [self.save])

			if header['Subject'] == None: header['Subject'] = '(No Subject)'
			header['Subject'] = unicode(header['Subject'], 'utf-8')
			print self.save

			self.database.execute('insert into mail (id,fromaddress,subject,toaddress,body) values (?,?,?,?,?)', [ self.save, header['From'], header['Subject'], header['To'], message ])
			self.db.commit()
		self.Mail = Database().mailread()

	def send(self, widget):
		body = self.buffer.get_text(self.buffer.get_start_iter(),self.buffer.get_end_iter())
		if self.Auth[5][1] != None:
			if self.mailcheck.get_active() == True:
				self.smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
				self.smtp.login(self.Auth[1][1], self.Auth[2][1])
				to = self.toentry.get_text()
				subject = self.subjectentry.get_text()
				self.smtp.sendmail(self.Auth[2][1], to, 'Subject: ' + subject + '\n' + body)
				self.smtp.quit()
		if self.twcheck.get_active() == True:
			self.Twitter.update_status(body)
		if self.fbcheck.get_active() == True:
			self.Facebook.put_wall_post(message=body,attachment={})			
		self.discard(0)

	def discard(self, widget):
		if self.Auth[5][1] != None:
			if self.mailcheck.get_active() == True:
				self.toentry.set_text('')
				self.subjectentry.set_text('')
		self.buffer.set_text('')
		self.charcount(0,0)

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

	def refresh(self, widget, widget2):
		''' Refreshes data. '''
		if self.Auth[1][1] != None: self.getmail()
		if self.Auth[3][1] != None:
			self.updatetwitter()
		tweets = ''
		for x in xrange(0, 17):
			tweets = tweets + '<div style="width: 100%; display: inline-block;"><span style="vertical-align: middle;"><br /><img src="' + self.twitterupdate[x].user.profile_image_url + '"></img></span><span style="float: right; width: 90%;"><p><b>' + self.twitterupdate[x].user.screen_name + '</b></p><p>' + self.twitterupdate[x].text + '</p></span><hr style="width: 100%;" /></div>'
		self.viewtw.load_html_string(tweets, 'file:///')
		fbposts = urllib.urlopen('https://graph.facebook.com/me/home?access_token=' + self.Auth[5][1])
		fbfeed = fbposts.read()
		fbposts.close()
		fbparsed = ''
		fbfeed = fbfeed.split('"',fbfeed.count('"'))
		for x in xrange(0,(len(fbfeed))):
			if fbfeed[x] == 'name':
				if fbfeed[x-2] == 'from': 
					fbparsed = fbparsed + '<p><b>' + fbfeed[x+2] + '</b></p>'
			if fbfeed[x] == 'message':
				fbparsed = fbparsed + '<p>' + fbfeed[x+2] + '</p><hr />'
		self.viewfb.load_html_string(fbparsed, 'file:///')

	def listmail(self, widget, widget2):
		''' Shows list of mail. '''
		if self.save < 50:
			for x in xrange(0,(self.save-1)):
				y = self.save - x
				msg = self.Mail[y][2] + ' - ' + self.Mail[y][1] + ' '*500 + str(x)
				self.iterator = self.model.prepend()
				self.model.set(self.iterator, 0, msg)
		else:
			for x in xrange(0,49):
				y = self.save + x - 50
				msg = self.Mail[y][2] + ' - ' + self.Mail[y][1] + ' '*500 + str(x)
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
		to = self.Mail[y][1].replace('<', '&lt;')
		to = to.replace('>', '&gt;')
		self.viewmail.load_html_string('<p>To: ' + to + '</p><p>Subject: ' + self.Mail[y][2] + '</p><hr />' +self.Mail[y][4], 'file:///')

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

	def loginfb(self):
		''' Logs into Facebook. '''
		self.Facebook = facebooksdk.GraphAPI(self.Auth[5][1])

	def main(self):
		''' This function will include the interface of Epistle, and all the function calls. '''
		gtk.main()


if __name__ == '__main__':
	app = Epistle()
	app.main()