#!/usr/bin/python
# -*- coding: utf-8 -*- 

def value_convertor(string):
    multiplier = 1
    if string[len(string) - 1] == "m":
        multiplier = 1000000
    elif string[len(string) - 1] == "k":
        multiplier = 1000
    integerPart = 0
    fractionalPart = 0
    numberOfFractionalDigits = 0
    doFractional = False
    for c in string:
        if c.isdigit():
            if doFractional:
                fractionalPart += int(c)
                fractionalPart *= 10
                numberOfFractionalDigits += 1
            else:
                integerPart += int(c)
                integerPart *= 10
                
        else:
            if c == ".":
                doFractional = True
    
    integerPart /= 10
    fractionalPart /= 10
    
    value = integerPart + (fractionalPart / 10.0 ** numberOfFractionalDigits)
    
    value *= multiplier
    
    return value

def singleQuoteFix(string):
    string = string.replace(";", "")
    string = string.replace("  ", " ")
    if string.__contains__("'"):
        string = string.replace("'", "''")
    for i in range(len(string) - 1, 0, -1):
        if (string[i] != ' '):
            break
    return string[:i+1]

def getAge(string):
    j = 0
    for i in range(0, len(string)):
        if string[i] == "(":
            j = i + 1
        if string[i] == ")":
            return string[j:i]

import sqlite3
import urllib2
import time
from bs4 import BeautifulSoup

# Get the time at which the program starts running.
start_time = time.time()

conn = sqlite3.connect("main.db")
print("Opened database successfully!")

# Remove the previous table.
conn.execute("DROP TABLE players")

print("Clean-up successful")

conn.execute("CREATE TABLE players (id INT PRIMARY KEY, name TEXT, team_id INT, position TEXT, age INT, nationality TEXT, value INT, href TEXT);")

print("Created table successfully")
print

opener = urllib2.build_opener()

# We need to add these in order to be able to access transfermarkt.
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

playerId = 0
playerIdPrevious = 0

cursor = conn.execute("SELECT * FROM teams;")

for row in cursor:
    teamId = int(row[0])
    teamName = row[1].encode('utf8')
    teamUrl = "http://www.transfermarkt.co.uk%s" % (row[6]) 
    leagueId = int(row[2])
    cursor2 = conn.execute("SELECT name, nation FROM leagues WHERE id = %s" % (leagueId))
    for row2 in cursor2:
        leagueName = row2[0]
        leagueNation = row2[1]
        
    handle = opener.open(teamUrl, None)
        
    # Use BeautifulSoup to parse the HTML file and pull data out of it.
    soup = BeautifulSoup(handle, "html.parser")
    parsed = soup('a')
    
    forRange = range (0, len(parsed))
    
    # NAME
    
    for i in forRange:
        try:
            if (parsed[i]['class'].__contains__("spielprofil_tooltip")):
                if (parsed[i].parent['class'][0].__contains__("hide-for-small")):
                    playerName = singleQuoteFix(parsed[i].string)
                    execute = "INSERT INTO players (id, name, team_id, href) VALUES (%s, '%s', '%s', '%s');" % (str(playerId), playerName, teamId, parsed[i]['href'])
                    conn.execute(execute)
                    playerId += 1
        except KeyError:
            continue        
    
    parsed = soup('img')
    
    forRange = range (0, len(parsed))
    playerId1 = playerIdPrevious
    trClass = u'even'
    
    # NATIONALITY
    
    for i in forRange:
        try:
            if (parsed[i]['class'].__contains__("flaggenrahmen") and
                parsed[i].parent.name == u'td' and
                parsed[i].parent.parent['class'][0] != trClass):
                conn.execute("UPDATE players SET nationality = '%s' WHERE id = %s;" % (singleQuoteFix(parsed[i]['title']), playerId1))
                playerId1 += 1
                if trClass == u'odd':
                    trClass = u'even'
                else:
                    trClass = u'odd'
        except KeyError:
            continue
    
    parsed = soup('td')
    playerId1 = playerIdPrevious
    playerId2 = playerIdPrevious
    forRange = range (11, len(parsed))
    
    # VALUE, AGE AND POSITION
    
    for i in forRange:
        try:
            if (len(parsed[i].contents) == 1 and 
                parsed[i].contents[0].string != None and
                not parsed[i].contents[0].string.isnumeric() and
                len(parsed[i].contents[0].string) > 1 and 
                not parsed[i].contents[0].__contains__("  ") and
                not parsed[i].has_attr("itemprop") and
                not parsed[i].contents[0].name == "b" and
                not parsed[i].has_attr("class") and
                not parsed[i].parent.parent.parent.name == "div"):
                    # In order for the code to work with the argentinian league, it needs the following check. For some reason, in the argentinian league a <td> is missing right after the position...
                    x = 0
                    if parsed[i + 1]['class'][0] == "hide":
                        x = 2
                    else:
                        x = 1
                    # End of fix for argentinian league.
                    forRange.remove(i + x)
                    playerPosition = parsed[i].contents[0].string
                    playerAge = getAge(parsed[i + x].contents[0])
                    if playerAge == None:
                        break
                    conn.execute("UPDATE players SET position = '%s' WHERE id = %s;" % (playerPosition, playerId2))
                    if not playerAge.__contains__("-"):
                        conn.execute("UPDATE players SET age = %s WHERE id = %s;" % (playerAge, playerId2))
                    else:
                        conn.execute("UPDATE players SET age = %s WHERE id = %s;" % (0, playerId2))
                    playerId2 += 1
            if (parsed[i]['class'].__contains__("rechts") and
                parsed[i]['class'].__contains__("hauptlink")):
                    if len(parsed[i].contents[0]) == 1:
                        conn.execute("UPDATE players SET value = %s WHERE id = %s;" % (0, playerId1))
                    else:
                        playerValue = value_convertor(parsed[i].contents[0][:len(parsed[i].contents[0]) - 1])
                        conn.execute("UPDATE players SET value = %s WHERE id = %s;" % (str(playerValue), playerId1))
                    playerId1 += 1
        except KeyError:
            continue
        
    playerIdPrevious = playerId
    print "Team id: %s. %s percent done. \n" % (teamId, str(round((teamId / 1584.0) * 100.0, 2)))
        

# Change some positions in order to minimise the total number of positions.        
conn.execute("UPDATE players SET position = 'Right Wing' WHERE position = 'Right Midfield'")
conn.execute("UPDATE players SET position = 'Centre Forward' WHERE position = 'Secondary Striker'")
conn.execute("UPDATE players SET position = 'Left Wing' WHERE position = 'Left Midfield'")
conn.execute("UPDATE players SET position = 'Central Midfield' WHERE position = 'Midfield'")
conn.execute("UPDATE players SET position = 'Centre Back' WHERE position = 'Defence'")
conn.execute("UPDATE players SET position = 'Centre Forward' WHERE position = 'Striker'")
conn.execute("UPDATE players SET position = 'Centre Back' WHERE position = 'Sweeper'")
conn.execute("UPDATE players SET position = 'Central Midfield' WHERE position = 'Mittelfeld'")
conn.execute("UPDATE players SET position = 'Centre Back' WHERE position = 'Abwehr'")
conn.execute("UPDATE players SET position = 'Centre Forward' WHERE position = 'Sturm'")
        
conn.commit()

print "Database created successfully, proccess took %s seconds." % (time.time() - start_time)

# Print all players.
cursor = conn.execute("SELECT * from players")
   
file = open('debug_players.txt', 'w')

for row in cursor:
    file.write("ID = %s\n" % row[0])
    file.write("NAME = %s\n" % row[1].encode('utf8'))
    file.write("TEAM ID = %s\n" % row[2])
    file.write("POSITION = %s\n" % row[3])
    file.write("AGE = %s\n" % row[4])
    file.write("NATIONALITY = %s\n" % row[5].encode('utf8'))
    file.write("VALUE = %s \n" % row[6])
    file.write("HREF = %s \n \n" % row[7])            
