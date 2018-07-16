import sqlite3

DBFILE = './db.sqlite'

conn = sqlite3.connect(DBFILE)

table1 = 'keypresses'

c = conn.cursor()

c.execute("""
CREATE TABLE `keypresses` (
	`ID`	INTEGER,
	`Q1`	INTEGER,
	`Q2`	INTEGER,
	`Q3`	INTEGER,
	`Q4`	INTEGER,
	`Q5`	INTEGER,
	`Q6`	INTEGER,
	`Q7`	INTEGER,
	PRIMARY KEY(`ID`)
);
""")

conn.commit()
conn.close()
