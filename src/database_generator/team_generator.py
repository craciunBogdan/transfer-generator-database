#!/usr/bin/python
# -*- coding: utf-8 -*-

def longest_spaceless_substring(string):
    longest = 0
    longestBegin = 0
    longestEnd = 1
    
    tempLength = 0
    tempBegin = 0
    tempEnd = 1
    if string.__contains__(" "):
        for c in string:
            if c == " " or c == "'":
                if tempLength >= longest:
                    longest = tempLength
                    longestBegin = tempBegin
                    longestEnd = tempEnd
                tempLength = 0
                tempEnd += 1
                tempBegin = tempEnd
            else:
                tempEnd += 1
                tempLength += 1
        if tempLength >= longest:
            longest = tempLength
            longestBegin = tempBegin
            longestEnd = tempEnd
        if longestBegin != 0:
            return string[(longestBegin - 1) : longestEnd - 1]
        else:
            return string[(longestBegin) : longestEnd - 1]
    else:
        return string

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
    
    return round(value, 2)

def singleQuoteFix(string):
    string = string.replace(";", "")
    if string.__contains__("'"):
        string = string.replace("'", "''")
    return string
#===============================================================================
# FIRST PART - Generating proper URLs for every team.
#===============================================================================

import time # Just to know how long it takes to build the database
import sqlite3
import urllib2
from bs4 import BeautifulSoup

# Get the time at which the program starts running.
start_time = time.time()

conn = sqlite3.connect("main.db")
print("Opened database successfully!")

# Remove the previous table.
conn.execute("DROP TABLE teams")

print("Clean-up successful")

    
conn.execute("CREATE TABLE teams (id INT PRIMARY KEY, name TEXT, league_id INT, squad_size INT, total_value INT, avg_value INT, href TEXT);")

print("Created table successfully")
print

opener = urllib2.build_opener()

# We need to add these in order to be able to access transfermarkt.
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

teamId = 0
teamId2 = 0

cursor = conn.execute("SELECT * FROM leagues;")
for row in cursor:
    leagueId = int(row[0])
    leagueName = row[1]
    leagueNation = row[2]
    leagueURL = "http://www.transfermarkt.co.uk%s" % (row[3])
    teamId2 = teamId
    print "Analysing %s (%s)." % (leagueName, leagueNation)
    
    handle = opener.open(leagueURL, None)
    
    # Use BeautifulSoup to parse the HTML file and pull data out of it.
    soup = BeautifulSoup(handle, "html.parser")
    parsed = soup('a')
    
    previousString = ""
    forRange = range (0, len(parsed))
    
    for i in forRange:
        try:
            if (parsed[i]['class'].__contains__("vereinprofil_tooltip") and
            parsed[i].string != None):
                if (parsed[i].parent['class'].__contains__(u'hide-for-small')):
                    if parsed[i].parent.parent.parent.parent.name == "div":
                        break
                    teamName = singleQuoteFix(parsed[i].string)
                    previousString = teamName
                    execute = "INSERT INTO teams (id, name, league_id, href) VALUES (%s, '%s', '%s', '%s');" % (str(teamId), teamName, str(leagueId), parsed[i]["href"])
                    conn.execute(execute)
                    teamId += 1
        except KeyError:
            continue
        
    # Set squad size, total value and avg value. Also delete teams that do not have a total value or a squad size.
    for i in range(0, len(parsed)):
        try:
            temporaryVariable = conn.execute("SELECT name FROM teams WHERE id = %s;" % (str(teamId2)))
            for row2 in temporaryVariable:
                name = row2[0]
            parsed[i]['title'] = parsed[i]['title'].replace("&amp;", "&")
            if parsed[i]['title'] == name:
                if (parsed[i].string == None or
                    (parsed[i+1].string == "-" and parsed[i].string.isnumeric())):
                    print ("DELETE FROM teams WHERE id IS %s" % str(teamId2))
                    conn.execute("DELETE FROM teams WHERE id IS %s" % str(teamId2))
                    teamId2 += 1
                    teamId -= 1
                elif parsed[i].string.isnumeric():
                    squadSize = int(parsed[i].string)
                    totalValue = value_convertor(parsed[i+1].string)
                    avgValue = round(totalValue / squadSize)
                    conn.execute("UPDATE teams SET squad_size = '%s' WHERE id = %s;" % (squadSize, str(teamId2)))
                    conn.execute("UPDATE teams SET total_value = '%s' WHERE id = %s;" % (totalValue, str(teamId2)))
                    conn.execute("UPDATE teams SET avg_value = '%s' WHERE id = %s;" % (avgValue, str(teamId2)))
                    teamId2 += 1
    
        except KeyError:
            continue

    
    print "{} ({}) successfully stored. {} % done. \n".format(leagueName.encode('utf8'), leagueNation, str(round((leagueId / 106.0) * 100.0, 2)))

conn.commit()
# Print the contents of the db. Mainly for debugging.
cursor = conn.execute("SELECT * from teams")
   
file = open('debug.txt', 'w')
   
for row in cursor:
    file.write("ID = %s\n" % row[0])
    file.write("NAME = %s\n" % row[1].encode('utf8'))
    file.write("LEAGUE ID = %s\n" % row[2])
    file.write("SQUAD SIZE = %s\n" % row[3])
    file.write("TOTAL VALUE = %s\n" % row[4])
    file.write("AVG VALUE = %s\n" % row[5])
    file.write("HREF = %s \n \n" % row[6])            

print "Database created successfully, proccess took %s seconds." % (time.time() - start_time)