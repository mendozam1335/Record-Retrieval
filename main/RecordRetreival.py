#!/usr/local/bin/python3
# -*- coding: UTF-8 -*-

from dbconfig import *
import pymysql
import cgi
import cgitb
cgitb.enable()

#	Connect to toyu of the MySQL server
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
    print('<h3>Levels With Swimmers</h3>')
    print('<ol>')

    query = '''
with test1 as (
select distinct l.LevelId as levelID, 
    l.Level as Level, 
    count(s.SwimmerId) as Amount,
    GROUP_CONCAT(concat('   <li><a href="?sid=', s.SwimmerId, '">',s.FName, ' ', 
    s.LName, '</a>: past level since ', LH.StartDate, '</li>\n') separator '') as History
from Swimmer s left join LevelHistory LH on (s.SwimmerId = LH.SwimmerId)
    left join Level l on (LH.LevelId = l.LevelId)
group by l.LevelId, l.Level),
test2 as
(select distinct l.LevelId as levelID, 
    l.Level as Level, 
    count(s.SwimmerId) as CurrentAmount,
    GROUP_CONCAT(concat('   <li><a href="?sid=', s.SwimmerId, '">',
    s.FName, ' ', s.LName, '</a>: current level since ', 
    H.StartDate, '</li>\n') separator '') as Current
from Swimmer s left join Level l on (s.CurrentLevelId = l.LevelId)
    inner join LevelHistory H on (l.LevelId = H.LevelId and s.SwimmerId = H.SwimmerId)
group by l.LevelId, l.Level)
select test1.levelID, test1.Level, test1.Amount, test1.History,
       test2.CurrentAmount, test2.Current
from test1 left join test2 on (test1.levelID = test2.levelID)
'''

    cursor.execute(query)


    def correctLevel(current:str, past:str):
        a = current.split('\n')
        b = past.split('\n')
        a.pop()
        b.pop()
        i = 0
        for x in b:
            for y in a:
                if y[21] == x[21]:
                    b[i] = b[i].replace('past', 'current')
            i = i + 1
        past = '\n'.join(b)
        past = past + '\n'
        return past

    for (lID, lvl, amt, history, c_amt, current) in cursor:
        print('   <li>Level #:' + str(lID) + ' (' + lvl + '): ' + str(amt) + ' achieved:<ol>')
        if c_amt:
            history = correctLevel(current, history)
        print(history + '</ol></li>')

    print('</ol>')
    print('</body></html>')
    cursor.close()
    cnx.close()
    quit()

else:
    query = '''
select distinct s.SwimmerId as ID, 
    concat(s.FName, ' ', s.LName) as Name,
    count(p.SwimmerId) as NumEvents,
    group_concat(concat('<li>',m.title, ': ', E.Title, '</li>\n') separator '') as Events
from Swimmer s left join Participation P on (s.SwimmerId = P.SwimmerId)
    inner join Event E on (P.EventId = E.EventId)
    inner join Meet M on (E.MeetId = M.MeetId)
where s.SwimmerId = %s
'''
    cursor.execute(query, (int(sid),))
    (id, name, num, events) = cursor.fetchone()

    print('<h3>Swimmer #' + str(id) + ' ' + name + ': participated in ' + str(num) + ' events.</h3>')
    print('<ol>' + events + '</ol>')

cursor.close()
cnx.close()

print('''</body>
</html>''')
