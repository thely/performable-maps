import sqlite3 as lite
import sys

con = lite.connect('test.db')

with con:
	cur = con.cursor()
	# cur.execute('SELECT SQLITE_VERSION()')
	# data = cur.fetchone()
	# print "SQLite version: %s" % data

	items = (
		(1, "ThisText"),
		(2, "MoreText"),
		(3, "tripleText"),
		(4, "One more for good measure")
	)

	cur.execute("DROP TABLE IF EXISTS Progress")
	cur.execute("CREATE TABLE Progress(Id INT, Name TEXT)")
	cur.executemany("INSERT INTO Progress VALUES(?, ?)", items)
	cur.execute("SELECT * FROM Progress")

	rows = cur.fetchall()

	for row in rows:
		print row[0]
