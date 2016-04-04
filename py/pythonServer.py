#!/usr/bin/python
import SimpleHTTPServer
import SocketServer
import cgi
import os.path
import logging
import sqlite3 as lite
import ttsqlite as db
from urlparse import urlparse, parse_qs
from pprint import pprint

PORT = 8080

class TTSServer(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		print "We're getting!"
		query = parse_qs(urlparse(self.path).query)
		if (not query):
			print "NO QUERY PRESENT; SERVE PAGE"
		elif (query['type'][0] == "clicks"):
			print "LET'S GET CLICKS"
		elif (query['type'][0] == "directions"):
			print "LET'S GET DIRECTIONS"
		else:
			print "INCORRECT QUERY TYPE"


		# form = cgi.FieldStorage()
		# pprint(vars(form))
		# self.send_head()
		# logging.error(self.headers)
		SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

	# Used for sending data to SqLite; the Maps stuff is complete,
	# and now we're storing it for when we need it.
	def do_POST(self):
		print "We're posting!"
		logging.error(self.headers)
		query = parse_qs(urlparse(self.path).query)
		form = cgi.FieldStorage(
			fp = self.rfile,
			headers = self.headers,
			environ = { 
				'REQUEST_METHOD': 'POST',
				'CONTENT_TYPE': self.headers['Content-Type']
			}
		)

		if (not query):
			return
		else:
			data = {}
			for item in form.list:
				# print "%s = %s" % (item.name, item.value)
				data[item.name] = item.value
			if (query['type'][0] == "clicks"):
				print "WE ARE POSTING NEW CLICKS"
				pprint(data)
				db.insert_clicks(data)
			elif (query['type'][0] == "directions"):
				print "WE ARE POSTING NEW DIRECTIONS"
				pprint(data)
				db.insert_text(data)
			else:
				print "I DON'T KNOW WHAT'S HAPPENING"
		
		self.wfile.write("<html><body><h1>POST!data</h1></body></html>")
		# """

	def end_headers(self):
		self.send_header("Access-Control-Allow-Origin", "*")
		SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)


Handler = TTSServer

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()	
