#!/usr/local/bin/python3
# -*- coding: UTF-8 -*-

from dbconfig import *
import pymysql
import cgi
import cgitb
cgitb.enable()

#	Establish a cursor for MySQL connection.
db = get_mysql_param()
cnx = pymysql.connect(user=db['user'],
                      password=db['password'],
                      host=db['host'],
                      # port needed only if it is not the default number, 3306.
                      # port = int(db['port']),
                      database=db['database'])

cursor = cnx.cursor()

#	Create HTTP response header
print("Content-Type: text/html;charset=utf-8")
print()

#	Create a primitive HTML starter
print('''<html>
<head></head>
<body>
''')

#	Get HTTP parameter, ctid (caretaker id) and sid (swimmer id)
form = cgi.FieldStorage()
sid = form.getfirst('sid')

if sid is None:
	#	No HTTP parameter: show all caretakers for selection.
	print('<h3>Please select from the following caretakers:</h3>')
	print('<ol>Caretakers:')

	query = '''
WITH t1 AS
(SELECT DISTINCT c.CT_Id,
	CONCAT(c.FName, ' ', c.LName) AS caretaker,
	COUNT(s.SwimmerId) AS n_primary_swimmer,
	GROUP_CONCAT(CONCAT('   <li><a href="?sid=', s.SwimmerId, '">',
		s.FName, ' ', s.LName, '</a></li>\n') SEPARATOR '') as primary_swimmers
FROM Caretaker AS c LEFT JOIN Swimmer AS S ON (c.CT_Id = s.Main_CT_Id)
GROUP BY c.CT_Id, caretaker),
t2 AS
(SELECT DISTINCT c.CT_Id,
	COUNT(o.SwimmerId) AS n_other_swimmer,
	GROUP_CONCAT(CONCAT('   <li><a href="?sid=', o.SwimmerId, '">',
		s.FName, ' ', s.LName, '</a></li>\n') SEPARATOR '') as other_swimmers
FROM Caretaker AS c LEFT JOIN OtherCaretaker AS o ON (c.CT_Id = o.CT_Id)
	LEFT JOIN Swimmer AS S ON (o.swimmerId = s.swimmerId)
GROUP BY c.CT_Id)
SELECT t1.CT_Id, t1.caretaker, t1.n_primary_swimmer, t1.primary_swimmers,
	t2.n_other_swimmer, t2.other_swimmers
FROM t1 LEFT JOIN t2 ON (t1.CT_id = t2.CT_Id);
'''
	cursor.execute(query)
	for (cid, caretaker, n_ps, ps, n_os, os) in cursor:
		print('    <li>caretakerId:' + str(cid) + ': ' + caretaker + ':<ul>')
		if (n_ps > 0):
			print('<li>primary caretaker for ' + str(n_ps) +
					' swimmer(s):<ol>' + ps + '</ol></li>')
		if (n_os > 0):
			print('<li>secondary caretaker for ' + str(n_os) +
					' swimmer(s):<ol>' + os + '</ol></li>')
		print('</ul></li>')
	
	print('</ol>')
	print('</body></html>')
	cursor.close()
	cnx.close()		
	quit()

else:	
	query = '''
SELECT DISTINCT s.lName, s.fName, l.level
FROM Swimmer AS s INNER JOIN Level AS l ON (s.CurrentLevelId = l.LevelId)
WHERE s.SwimmerId = %s
'''

	cursor.execute(query,(int(sid),))
	(lname, fname, level) = cursor.fetchone()
	
	print('<p>Swimmer #' + str(sid) + ', ' +
			 fname + ' ' + lname + ': current level: ' + level)
                  
cursor.close()
cnx.close()		
				  
print ('''</body>
</html>''')
