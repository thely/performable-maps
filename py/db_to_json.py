import sqlite3 as lite
import sys
import json

con = lite.connect('text2speech.db')
con.row_factory = lite.Row

with con:
	cur = con.cursor()

	cur.execute("SELECT * FROM Path")

	shell = []
	while True:
		row = cur.fetchone()

		if row == None:
			break

		cols = row.keys()
		line = {}
		line[cols[0]] = row[0]
		line[cols[1]] = row[1]
		line[cols[2]] = row[2]
		shell.append(line)
		# print cols[1], ": ", row[1]
		# print cols[2], ": ", row[2]

	with open('tts_json.txt', 'w') as outfile:
		json.dump(shell, outfile, indent=4)
