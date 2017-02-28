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

def get_directionslist():
	con = start_db()
	with con:
		cur = con.cursor()
		cur.execute("SELECT Id, Start, End, Date_Created FROM Path")
		rows = cur.fetchall()
		json_ret = { "paths": [] }
		for row in rows:
			json_ret["paths"].append({ 
					"path_id": row[0], 
					"start": row[1], 
					"end": row[2], 
					"date_created": row[3]
			})

		return json_ret

def get_directions(path_id):
	con = start_db()
	with con:
		cur = con.cursor()
		sel_statement = "SELECT * FROM Steps WHERE Path_Id = \"" + str(path_id + "\"")
		# pprint(sel_statement)
		cur.execute(sel_statement)

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

		# cur.execute("DROP TABLE IF EXISTS Path")
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
		cur.execute("CREATE TABLE IF NOT EXISTS Clicks(Path_Id TEXT, Step_Id INT, Click_Id INT, Voice_Type TEXT, TimeAdded INT, Checked INT)")

		tupler = (data['path_id'], data['step_id'], data['click_id'], data['voice_type'], data['timestamp'], data['checked'])
		cur.execute("INSERT INTO Clicks VALUES(?, ?, ?, ?, ?, ?)", tupler)
		cur.execute("SELECT * FROM Clicks")

		rows = cur.fetchall()

		for row in rows:
			print row[0]

def get_click():
	con = start_db()
	with con:
		cur = con.cursor()
		cur.execute("SELECT min(TimeAdded) FROM Clicks WHERE Checked = 0")
		timestamp = cur.fetchone()[0]
		if (timestamp == None):
			return { "error_name": "No clicks", "error_desc": "Ran out of clicks. Wait for more."}

		cur.execute("SELECT * FROM Clicks WHERE Checked = 0 AND TimeAdded = " + str(timestamp) + " LIMIT 1")

		row = cur.fetchone()
		# pprint(row)
		json_ret = { "path_id": row[0], "step_id": row[1], "click_id": row[2], "voice_type": row[3], "timestamp": row[4] }

		cur.execute("SELECT Instructions FROM Steps WHERE Path_Id = \"" + json_ret["path_id"] + "\" AND Step_Id = " + str(json_ret["step_id"]))
		json_ret["text"] = cur.fetchone()[0]

		cur.execute("UPDATE Clicks SET Checked = 1 WHERE Click_Id = " + str(json_ret['click_id']))
		return json_ret

def insert_speechtrigger(data):
	con = start_db()
	with con:
		cur = con.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS SpeechTrigger(Type TEXT, Time INT, Checked INT)")
		cur.execute("INSERT INTO SpeechTrigger VALUES(?, ?, ?)", (data['type'], data['time'], data['checked']))

def get_speechtrigger():
	con = start_db()
	with con:
		cur = con.cursor()
		cur.execute("SELECT min(Time), Type FROM SpeechTrigger WHERE Checked = 0")
		row = cur.fetchone()
		if (row[0] == None):
			return { "result": "failure", "type": "error", "error_desc": "Ran outta boundaries. Wait for more."}

		cur.execute("UPDATE SpeechTrigger SET Checked = 1 WHERE Time = " + str(row[0]))

		return { "result": "success", "timestamp": row[0], "type": row[1] }

def insert_voices(data):
	con = start_db()
	with con:
		cur = con.cursor()
		cur.execute("DROP TABLE IF EXISTS VoiceList")
		cur.execute("CREATE TABLE IF NOT EXISTS VoiceList(Id INT, VoiceName TEXT)")

		# pprint(data)

		voicelist = []
		for i in data:
			# pprint(i)
			# pprint(data[i])
			voicelist.append((int(i), unicode(data[i])))

		pprint(voicelist)
		cur.executemany("INSERT INTO VoiceList VALUES(?, ?)", voicelist)
		pprint("DONE INSERTING VOICES?")

def clear_performance_data():
	con = start_db()
	cur.execute("DROP TABLE IF EXISTS Clicks")
	cur.execute("DROP TABLE IF EXISTS SpeechTrigger")

def get_voices():
	con = start_db()
	with con:
		cur = con.cursor()
		cur.execute("SELECT * FROM VoiceList")
		rows = cur.fetchall()
		json_ret = {}
		json_ret['voices'] = [None] * len(rows)
		# pprint("Length of json_ret is " + str(len(json_ret)))

		for row in rows:
			pprint(row)
			json_ret['voices'][row[0]] = str(row[1])

		return json_ret

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



