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
		if (not query or 'obj' not in query or 'type' not in query): # Loading the browser window
			print "NO QUERY PRESENT; SERVE PAGE"
			SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
		else:
			obj = query['obj'][0]
			typ = query['type'][0]

			# Look through the endpoints
			if (obj == "maps"):
				if (typ == "steps"):
					print "LET'S GET DIRECTIONS"
					self.get_response(db.get_directions, query['path-id'][0])
				elif (typ == "paths"): # Max getting all paths currently stored
					if ("action" in query):
						print "Making a new map, fresh from Max"
					self.get_response(db.get_directionslist)
				else:
					print "MAPS: Incorrect query type"

			elif (obj == "voice"): # Browser sending voice data
				if (typ == "voicelist"):
					print "GETTING VOICE LIST"
					self.get_response(db.get_voices)
				elif (typ == "triggers"):
					act = query['action'][0]
					if (act == "utter"): # Browser polling for clicks
						print "LET'S GET A DANG CLICK"
						self.get_response(db.get_click)
						# self.wfile.write(json.dumps(db.get_click()))
					elif (act == "boundary"):
						print "CHECKING BOUNDARY"
						self.get_response(db.get_speechtrigger)
				else:
					print "VOICE: Incorrect query type"
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

		if (not query or 'obj' not in query or 'type' not in query):
			return
		else:
			obj = query['obj'][0]
			typ = query['type'][0]
			data = {}
			for item in form.list:
				data[item.name] = item.value

			if (obj == "maps"):
				if (typ == "paths"):
					print "ADDING NEW PATH"
					db.insert_text(data)
			elif (obj == "voice"):
				if (typ == "voicelist"):
					print "ADDING VOICE LIST"
					db.insert_voices(data)
				elif (typ == "triggers"):
					print "POSTING A TRIGGER"
					act = query['action'][0]
					if (act == "utter"):
						print "FAKING A CLICK"
						db.insert_clicks(data)
					elif (act == "boundary"):
						print "CHECKING SPEECHSYNTH BOUNDARY"
						db.insert_speechtrigger(data)
			else:
				print "POST: Incorrect query type"
		
		self.wfile.write("<html><body><h1>POST!data</h1></body></html>")
		# """

	def get_response(self, get_func, *args):
		self.send_response(200)
		self.send_header('Content-Type', 'application/json')
		self.end_headers()
		self.wfile.write(json.dumps(get_func(*args)))

	def end_headers(self):
		self.send_header("Access-Control-Allow-Origin", "*")
		SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)


reload(sys)
sys.setdefaultencoding("utf-8")

Handler = TTSServer
httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()	
