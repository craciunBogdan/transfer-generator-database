#!/usr/bin/python
# -*- coding: utf-8 -*- 

# Import necessary libraries for web crawling and database manipulation
import time # Just to know how long it takes to build the database
import urllib2
from bs4 import BeautifulSoup
import sqlite3

# Get the time at which the program starts running.
start_time = time.time()

# Create the db.
conn = sqlite3.connect("main.db")

print("Opened database successfully!")

# Remove the old table.
conn.execute("DROP TABLE leagues")

print("Clean-up successful")

# Create a new table.
conn.execute("CREATE TABLE leagues (id INT PRIMARY KEY, name TEXT, nation TEXT, href TEXT);")

print("Created table successfully")

# The URL from which we want to get the information to store in the db.
tmUrl = "http://www.transfermarkt.co.uk/wettbewerbe/europa/wettbewerbe"

opener = urllib2.build_opener()

# We need to add these in order to be able to access transfermarkt.
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

handle = opener.open(tmUrl, None)

# Use BeautifulSoup to parse the HTML file and pull data out of it.
soup = BeautifulSoup(handle, "html.parser")

parsed = soup('img')

# Variable that keeps count of the next id available.
leagueId = 0

forRange = range (0, len(parsed))

# Insert the leagues into the db (with id, name and nation).
for i in forRange:
    try:
        if ((parsed[i]['title'] != "Go to competition forum") and 
        (not parsed[i]['title'].__contains__("EURO")) and 
        (not parsed[i]['title'].__contains__("Euro")) and 
        (not parsed[i]['title'].__contains__("UEFA")) and
        (parsed[i]['title'] != "Navigation") and
        (parsed[i]['title'] != "Advanced player search")):
            #execute = "INSERT INTO leagues (id, name, nation) VALUES (" + str(leagueId) + ", '" + parsed[i]['title'] + "', '" + parsed[i + 1]['title'] + "');"
            execute = "INSERT INTO leagues (id, name, nation) VALUES (%s, '%s', '%s');" % (str(leagueId), parsed[i]['title'], parsed[i + 1]['title'])
            conn.execute(execute)
            leagueId += 1
            forRange.remove(i + 1)
    except KeyError:
        continue

leagueId2 = 0

# Get the href row filled in the db by searching for the necessary links using the name of the leagues from the db.
parsed = soup('a')

for i in range(0, len(parsed)):
    try:
        #temporaryVariable = conn.execute("SELECT name FROM leagues WHERE id = " + str(leagueId2) + ";")
        temporaryVariable = conn.execute("SELECT name FROM leagues WHERE id = %s;" % (str(leagueId2)))
        for row in temporaryVariable:
            name = row[0]
            
        if parsed[i]['title'] == name:
            href = parsed[i]['href']
            #conn.execute("UPDATE leagues SET href = '" + href + "' WHERE id = " + str(leagueId2) + ";")
            conn.execute("UPDATE leagues SET href = '%s' WHERE id = %s;" % (href, str(leagueId2)))
            leagueId2 += 1

    except KeyError:
        continue

# Change the URL to the second page. The rest of the code is the same as before.
tmUrl = "http://www.transfermarkt.co.uk/wettbewerbe/europa?page=2"

handle = opener.open(tmUrl, None)

soup = BeautifulSoup(handle, "html.parser")

parsed = soup('img')

forRange = range (0, len(parsed))

for i in forRange:
    try:
        if ((parsed[i]['title'] != "Go to competition forum") and 
        (not parsed[i]['title'].__contains__("EURO")) and 
        (not parsed[i]['title'].__contains__("Euro")) and 
        (not parsed[i]['title'].__contains__("UEFA")) and
        (parsed[i]['title'] != "Navigation") and
        (parsed[i]['title'] != "Advanced player search")):
            execute = "INSERT INTO leagues (id, name, nation) VALUES (%s, '%s', '%s');" % (str(leagueId), parsed[i]['title'], parsed[i + 1]['title'])
            conn.execute(execute)
            leagueId += 1
            forRange.remove(i + 1)
    except KeyError:
        continue
    
parsed = soup('a')

for i in range(0, len(parsed)):
    try:
        temporaryVariable = conn.execute("SELECT name FROM leagues WHERE id = %s;" % (str(leagueId2)))
        
        for row in temporaryVariable:
            name = row[0]
            
        if parsed[i]['title'] == name:
            href = parsed[i]['href']
            conn.execute("UPDATE leagues SET href = '%s' WHERE id = %s;" % (href, str(leagueId2)))
            leagueId2 += 1

    except KeyError:
        continue

# Change the URL to the third page. The rest of the code is the same as before.
tmUrl = "http://www.transfermarkt.co.uk/wettbewerbe/europa?page=3"

handle = opener.open(tmUrl, None)

soup = BeautifulSoup(handle, "html.parser")

parsed = soup('img')

forRange = range (0, len(parsed))

for i in forRange:
    try:
        if ((parsed[i]['title'] != "Go to competition forum") and 
        (not parsed[i]['title'].__contains__("EURO")) and 
        (not parsed[i]['title'].__contains__("Euro")) and 
        (not parsed[i]['title'].__contains__("UEFA")) and
        (parsed[i]['title'] != "Navigation") and
        (parsed[i]['title'] != "Advanced player search")):
            execute = "INSERT INTO leagues (id, name, nation) VALUES (%s, '%s', '%s');" % (str(leagueId), parsed[i]['title'], parsed[i + 1]['title'])  
            conn.execute(execute)
            leagueId += 1
            forRange.remove(i + 1)
    except KeyError:
        continue
    
parsed = soup('a')

for i in range(0, len(parsed)):
    try:
        temporaryVariable = conn.execute("SELECT name FROM leagues WHERE id = %s;" % (str(leagueId2)))
        
        for row in temporaryVariable:
            name = row[0]
            
        if parsed[i]['title'] == name:
            href = parsed[i]['href']
            conn.execute("UPDATE leagues SET href = '%s' WHERE id = %s;" % (href, str(leagueId2)))
            leagueId2 += 1

    except KeyError:
        continue

# Change the URL to the Asian competitions page. The rest of the code is the same as before with the exception of the break in the for loop which stops it when reaching the second divisions.
tmUrl = "http://www.transfermarkt.co.uk/wettbewerbe/asien"

handle = opener.open(tmUrl, None)

soup = BeautifulSoup(handle, "html.parser")

parsed = soup('img')

forRange = range (0, len(parsed))

for i in forRange:
    try:
        if (parsed[i]['title'] == "China League One"):
            break
        elif (parsed[i]['title'] == "J1 League - Second Stage"):
            forRange.remove(i + 1)
        elif ((parsed[i]['title'] != "Go to competition forum") and 
        (not parsed[i]['title'].__contains__("OFC")) and 
        (not parsed[i]['title'].__contains__("AFC")) and 
        (not parsed[i]['title'].__contains__("Cup")) and
        (not parsed[i]['title'].__contains__("East Asian")) and
        (parsed[i]['title'] != "Navigation") and
        (parsed[i]['title'] != "Advanced player search")):
            execute = "INSERT INTO leagues (id, name, nation) VALUES (%s, '%s', '%s');" % (str(leagueId), parsed[i]['title'], parsed[i + 1]['title'])
            conn.execute(execute)
            leagueId += 1
            forRange.remove(i + 1)
    except KeyError:
        continue
    
parsed = soup('a')

for i in range(0, len(parsed)):
    try:
        temporaryVariable = conn.execute("SELECT name FROM leagues WHERE id = %s;" % (str(leagueId2)))
        
        for row in temporaryVariable:
            name = row[0]
            
        if parsed[i]['title'] == name:
            href = parsed[i]['href']
            conn.execute("UPDATE leagues SET href = '%s' WHERE id = %s;" % (href, str(leagueId2)))
            leagueId2 += 1

    except KeyError:
        continue

# Change the URL to the American competitions page. The rest of the code is the same as before with the exception of the break in the for loop which stops it when reaching the second divisions.
tmUrl = "http://www.transfermarkt.co.uk/wettbewerbe/amerika"

handle = opener.open(tmUrl, None)

soup = BeautifulSoup(handle, "html.parser")

parsed = soup('img')

forRange = range (0, len(parsed))

for i in forRange:
    try:
        if (parsed[i]['title'] == "Ascenso MX Clausura"):
            break
        
        elif ((parsed[i]['title'] == "Liga MX Clausura") or
        (parsed[i]['title'].__contains__("II")) or
        (parsed[i]['title'].__contains__("Invierno")) or
        (parsed[i]['title'] == "Serie A Segunda Etapa") or
        (parsed[i]['title'] == "Torneo Clausura")):
            forRange.remove(i + 1)
            
        elif ((parsed[i]['title'] != "Go to competition forum") and 
        (not parsed[i]['title'].__contains__("CONCACAF")) and 
        (not parsed[i]['title'].__contains__("Copa")) and 
        (not parsed[i]['title'].__contains__("Cup")) and
        (not parsed[i]['title'].__contains__("Uruguayo")) and
        (not parsed[i]['title'].__contains__("Uruguay")) and
        (parsed[i]['title'] != "Navigation") and
        (parsed[i]['title'] != "Advanced player search")):
            execute = "INSERT INTO leagues (id, name, nation) VALUES (%s, '%s', '%s');" % (str(leagueId), parsed[i]['title'], parsed[i + 1]['title'])
            conn.execute(execute)
            leagueId += 1
            forRange.remove(i + 1)
    except KeyError:
        continue
    
parsed = soup('a')

for i in range(0, len(parsed)):
    try:
        temporaryVariable = conn.execute("SELECT name FROM leagues WHERE id = %s;" % (str(leagueId2)))
        
        for row in temporaryVariable:
            name = row[0]
            
        if parsed[i]['title'] == name:
            href = parsed[i]['href']
            conn.execute("UPDATE leagues SET href = '%s' WHERE id = %s;" % (href, str(leagueId2)))
            leagueId2 += 1

    except KeyError:
        continue

# Change the URL to the African competitions page. The rest of the code is the same as before.
tmUrl = "http://www.transfermarkt.co.uk/wettbewerbe/afrika"

handle = opener.open(tmUrl, None)

soup = BeautifulSoup(handle, "html.parser")

parsed = soup('img')

forRange = range (0, len(parsed))

for i in forRange:
    try:
        if (parsed[i]['title'] == "MTN8"):
            break
        
        if ((parsed[i]['title'] != "Go to competition forum") and 
        (not parsed[i]['title'].__contains__("CAF")) and 
        (not parsed[i]['title'].__contains__("Cup")) and 
        (parsed[i]['title'] != "Navigation") and
        (parsed[i]['title'] != "Advanced player search")):
            execute = "INSERT INTO leagues (id, name, nation) VALUES (%s, '%s', '%s');" % (str(leagueId), parsed[i]['title'], parsed[i + 1]['title'])
            conn.execute(execute)
            leagueId += 1
            forRange.remove(i + 1)
    except KeyError:
        continue
    
parsed = soup('a')

for i in range(0, len(parsed)):
    try:
        temporaryVariable = conn.execute("SELECT name FROM leagues WHERE id = %s;" % (str(leagueId2)))
        
        for row in temporaryVariable:
            name = row[0]
            
        if parsed[i]['title'] == name:
            href = parsed[i]['href']
            conn.execute("UPDATE leagues SET href = '%s' WHERE id = %s;" % (href, str(leagueId2)))
            leagueId2 += 1

    except KeyError:
        continue


conn.commit()

print("Records created successfully")


# Print the contents of the db. Mainly for debugging.
cursor = conn.execute("SELECT * from leagues")
 
for row in cursor:
    print "ID = ", row[0]
    print "NAME = ", row[1]
    print "NATION = ", row[2]
    print "HREF = ", row[3], '\n'

# Print how much it took to build the database.
print "Database created successfully, proccess took %s seconds." % (time.time() - start_time)