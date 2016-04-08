#!/usr/bin/python
import SimpleHTTPServer
import SocketServer
import cgi
import sys
import os.path
import logging
import json
import sqlite3 as lite
import ttsqlite as db
from urlparse import urlparse, parse_qs
from pprint import pprint

PORT = 8080

class TTSServer(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		print "We're getting!"
		query = parse_qs(urlparse(self.path).query)
		pprint(query)
		if (not query): # Loading the browser window
			print "NO QUERY PRESENT; SERVE PAGE"
			SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
		elif (query['type'][0] == "clicks"): # Browser polling for clicks
			print "LET'S GET A DANG CLICK"
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps(db.get_click()))
		elif (query['type'][0] == "steps"): # Max getting all steps for a path
			print "LET'S GET DIRECTIONS"
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps(db.get_directions(query['path-id'][0])))
		elif (query['type'][0] == "paths"): # Max getting all paths currently stored
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps(db.get_directionslist()))
		elif (query['type'][0] == "speak"): # Browser sending voice data
			ask = query['ask'][0]
			if (ask == "voicelist"):
				print "GETTING VOICE LIST"
				self.send_response(200)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				self.wfile.write(json.dumps(db.get_voices()))
			elif (ask == "triggers"):
				print "POSTING VOICE START/END"
		else:
			print "INCORRECT QUERY TYPE"


		# form = cgi.FieldStorage()
		# pprint(vars(form))
		# self.send_head()
		# logging.error(self.headers)

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
				data[item.name] = item.value
			if (query['type'][0] == "clicks"): # Max sending a click to the browser
				print "WE ARE POSTING NEW CLICKS"
				pprint(data)
				db.insert_clicks(data)
			elif (query['type'][0] == "paths"): # Max/browser saving new paths/steps
				print "WE ARE POSTING NEW DIRECTIONS"
				pprint(data)
				db.insert_text(data)
			elif (query['type'][0] == "speak"): # Browser sending voice data
				ask = query['ask'][0]
				if (ask == "voicelist"):
					print "POSTING VOICE LIST"
					db.insert_voices(data)
				elif (ask == "triggers"):
					print "POSTING VOICE START/END"
			else:
				print "I DON'T KNOW WHAT'S HAPPENING"
		
		self.wfile.write("<html><body><h1>POST!data</h1></body></html>")
		# """

	def end_headers(self):
		self.send_header("Access-Control-Allow-Origin", "*")
		SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)


reload(sys)
sys.setdefaultencoding("utf-8")

Handler = TTSServer
httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()	
