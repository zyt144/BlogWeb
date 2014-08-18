#!/usr/bin/env python

import webapp2
import jinja2
import os
import datetime
import re

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api import app_identity
from datetime import datetime


template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)
	


class Blog(webapp2.RequestHandler):

	def get(self):
		login_url = users.create_login_url(self.request.uri)
		logout_url = users.create_logout_url(self.request.uri)

		posts = db.GqlQuery("SELECT * FROM Post ORDER BY adddate DESC LIMIT 10")
		posts_dic = {"posts" : posts,  "login_url": login_url, "logout_url": logout_url}
		self.response.out.write(render_str('blog.html', **posts_dic))
		
class Readmore(webapp2.RequestHandler):

	def get(self):
		ptime = self.request.get('time')
		psubject = self.request.get('subject')
		pcontent = self.request.get('content')
		ptag = self.request.get('tag')
		
		post = Post(title=psubject,body=pcontent,tag=ptag,time=ptime)
		posts = [post]
		posts_dic = {"posts": posts}
		self.response.out.write(render_str('readmore.html', **posts_dic))
		
class Search(webapp2.RequestHandler):

	def get(self):
		stag=self.request.get("tag")
		posts = db.GqlQuery("SELECT * FROM Post WHERE tagli=:1 ORDER BY adddate DESC LIMIT 10" ,stag )
		posts_dic = {"posts": posts, "stag":stag}
		self.response.out.write(render_str('search.html', **posts_dic))
		
class Searcholder(webapp2.RequestHandler):

	def get(self):
		stag=self.request.get("tag")
		posts = db.GqlQuery("SELECT * FROM Post WHERE tagli=:1 ORDER BY adddate DESC" ,stag )
		posts_dic = {"posts": posts}
		self.response.out.write(render_str('searcholder.html', **posts_dic))
		
class Older(webapp2.RequestHandler):
	def get(self):

		posts = db.GqlQuery("SELECT * FROM Post ORDER BY adddate DESC")
		posts_dic = {"posts" : posts}
		self.response.out.write(render_str('older.html', **posts_dic))
	
		
class Rss(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/xml'

		logout_url = users.create_logout_url(self.request.uri)
		server_url = app_identity.get_default_version_hostname()

		posts = db.GqlQuery("SELECT * FROM Post ORDER BY adddate DESC LIMIT 10")
		posts_dic = {"posts" : posts, "logout_url": logout_url, "server_url": server_url}
		self.response.out.write(render_str('rss.xml', **posts_dic))
		
		
class Create(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			self.response.out.write(render_str('create.html'))
		else:
			greeting = ('<a href="%s">Sign in or register</a>.' %
						users.create_login_url('/'))
			self.response.out.write('<html><body>%s</body></html>' % greeting)
	
	def post(self):
		user = users.get_current_user().nickname()
		subject = self.request.get('subject')
		content = self.request.get('content')
		briefs = content[0:500]
		tags = self.request.get('tags')
		tagst = tags.split(',')
		tagsli=[]
		for t in tagst:
			tt=t.encode('ascii','ignore')
			tagsli.append(tt)
		time = unicode(datetime.now().replace(microsecond=0))
		images = self.request.get('img').encode('ascii','ignore')
		imaget = db.Blob(images)
		
		blog_post = Post(author= user, title=subject, body=content, tag=tags,tagli=tagsli,brief=briefs,time=time, image=imaget)
		blog_post.put()
		self.redirect('/')
		
class Edit(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		pauthor = self.request.get('author')
		ptime = self.request.get('time')
		psubject = self.request.get('subject')
		pcontent = self.request.get('content')
		ptag = self.request.get('tag')
		ptagt = ptag.split(',')
		ptagli=[]
		for t in ptagt:
			tt=t.encode('ascii','ignore')
			ptagli.append(tt)
		pbrief = self.request.get('brief')
		
		if user:
			if (user.nickname() == pauthor):
				post = Post(author =pauthor,title=psubject,body=pcontent,tag=ptag,tagli=ptagli,brief=pbrief,time=ptime)
				posts = [post]
				posts_dic = {"posts" : posts}
				self.response.out.write(render_str('edit.html', **posts_dic))

			else:
				back = ('<a href="/">Back to Home</a>')
				self.response.out.write('<html><body>You can not edit post written by someone else! <br/>%s</body></html>' %back)
		else:
			greeting = ('<a href="%s">Sign in or register</a>.' %
						users.create_login_url('/'))
			self.response.out.write('<html><body>%s</body></html>' % greeting)
	
	def post(self):
		user = users.get_current_user().nickname()
		subject = self.request.get('subject')
		content = self.request.get('content')
		briefs = content[0:500]
		tags = self.request.get('tags')
		time = unicode(datetime.now().replace(microsecond=0))
		blog_post = Post(title=subject, body=content, tag=tags,brief=briefs,time=time,author = user)
		blog_post.put()
		self.redirect('/')

class Post(db.Model):
	author = db.StringProperty()
	title = db.StringProperty(required=True)
	body = db.TextProperty(required=True)
	brief = db.TextProperty()
	tag = db.StringProperty()
	tagli = db.StringListProperty()
	adddate = db.DateTimeProperty(auto_now_add=True)
	time = db.StringProperty()
	image = db.BlobProperty()
	
	
		
application = webapp2.WSGIApplication([
    ('/', Blog),
	('/create', Create),
	('/rss', Rss),
	('/older', Older),
	('/edit', Edit),
	('/search', Search),
	('/searcholder',Searcholder),
	('/readmore',Readmore)
], debug=True)