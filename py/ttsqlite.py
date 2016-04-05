import sqlite3 as lite
import sys
import uuid
from datetime import datetime
import calendar
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
		new_pathID = str(uuid.uuid4())
		items = format_data(data, new_pathID)

		pprint(items[0])
		pprint(items[1])

		cur.execute("DROP TABLE IF EXISTS Path")
		cur.execute("CREATE TABLE IF NOT EXISTS Path(Id TEXT, Date_Created INT, Start TEXT, End TEXT, Distance TEXT, Step_Count TEXT)")
		cur.execute("CREATE TABLE IF NOT EXISTS Steps(Path_Id TEXT, Step_Id INT, Instructions TEXT, Distance INT)")
		cur.execute("INSERT INTO Path VALUES(?, ?, ?, ?, ?, ?)", items[0])
		cur.executemany("INSERT INTO Steps VALUES(?, ?, ?, ?)", items[1])
		cur.execute("SELECT * FROM Steps")

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
		

def format_data(data, path_id):
	# Make a shell for the data
	length = int(data['num_steps'])
	right_now = calendar.timegm(datetime.utcnow().utctimetuple())
	items = [{"path_id": path_id, "index": 0, "text": "", "dist": 0} for x in range(0, length)]
	path_info = {"path_id": path_id, "time": right_now, "num_steps": 0, "distance": 0, "start": "", "end": ""}
	# print data['num_steps']

	# Format data to fit the shell
	for x in range(0, length):
		items[x]['index'] = x
		for key in data:
			if (key.startswith(str(x) + "-text")):
				items[x]['text'] = data[key]
			elif (key.startswith(str(x) + "-dist")):
				items[x]['dist'] = data[key]
			else:
				path_info[key] = data[key]

	# Tuple the data so SqLite will accept it
	path_tuple = (path_info['path_id'], path_info['time'], path_info['start'], path_info['end'], path_info['distance'], path_info['num_steps'])
	steps_tupler = []
	for item in items:
		steps_tupler.append((item['path_id'], item['index'], item['text'], int(item['dist'])))

	doubletupler = (path_tuple, steps_tupler)
	return doubletupler



