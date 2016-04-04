import sqlite3 as lite
import sys
from pprint import pprint

def start_db():
	con = lite.connect('text2speech.db')
	return con


# Used to add the list of directions to the Path table.
# Since there is no way to append extra directions when
# a route is complete, the table should be dropped if a new
# path is generated for a given performance.

def get_directions():
	con = start_db()
	with con:
		cur = con.cursor()
		cur.execute("SELECT * FROM Path")

		rows = cur.fetchall()
		json_ret = { "steps" : [] }
		for row in rows:
			json_ret["steps"].append({ "text": row[1], "dist": row[2] })

		return json_ret

def insert_text(data):
	con = start_db()
	with con:
		cur = con.cursor()
		items = format_data(data)

		cur.execute("DROP TABLE IF EXISTS Path")
		cur.execute("CREATE TABLE Path(Id INT, Instructions TEXT, Distance INT)")
		cur.executemany("INSERT INTO Path VALUES(?, ?, ?)", items)
		cur.execute("SELECT * FROM Path")

		"""
		rows = cur.fetchall()

		for row in rows:
			print row[0]
		"""

def insert_clicks(data):
	con = start_db()
	with con:
		cur = con.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS Clicks(ClickId INT, StepId INT, TimeAdded INT, Checked INT)")

		tupler = (data['click_id'], data['step_id'], data['timestamp'], data['checked'])
		cur.execute("INSERT INTO Clicks VALUES(?, ?, ?, ?)", tupler)
		cur.execute("SELECT * FROM Clicks")

		rows = cur.fetchall()

		for row in rows:
			print row[0]
		

def format_data(data):
	# Make a shell for the data
	length = int(data['num_steps'])
	items = [{"index": 0, "text": "", "dist": 0} for x in range(0, length)]
	# print data['num_steps']

	# Format data to fit the shell
	for x in range(0, length):
		items[x]['index'] = x
		for key in data:
			if (key.startswith(str(x) + "-text")):
				items[x]['text'] = data[key]
			elif (key.startswith(str(x) + "-dist")):
				items[x]['dist'] = data[key]

	# Tuple the data so SqLite will accept it
	tupler = []
	for item in items:
		tupler.append((item['index'], item['text'], int(item['dist'])))
	return tupler



