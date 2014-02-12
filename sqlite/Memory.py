import sqlite3
import cPickle
import os
import random
import time
import Text
import sys

MEMPATH = os.getcwd()
BUFFSIZE = 150
TIMEFRAME = 5
POSSIBLEMAX = 10
MAXDUP = 3

def OpenMemory(botname):
	dbfilename = os.path.join(MEMPATH, botname + '.sqlite3')
	chfilename = os.path.join(MEMPATH, botname + '.cache')
	db = sqlite3.connect(dbfilename)
	c = db.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS memory(id INTEGER PRIMARY KEY, value TEXT)')
	db.commit()
	try:
		chfile = open(chfilename,'r')
	except IOError:
		cache = {}
		c.execute('SELECT Count(*) FROM memory')
		if c.fetchone()[0] != 0:
			for key, val in c.execute('SELECT id, value FROM memory'):
				if val in cache:
					cache[val].append(key)
				else:
					cache[val] = [key]
	else:
		cache = cPickle.load(chfile)
		chfile.close()
		os.remove(chfilename)
	return (db, cache)

def CloseMemory(memorytuple, botname):
	db, cache = memorytuple
	chfilename = os.path.join(MEMPATH, botname + '.cache')
	db.commit()
	db.close()
	chfile = open(chfilename,'w')
	cPickle.dump(cache, chfile)
	chfile.close()

def InsertMemory(memorytuple, string):
	db, cache = memorytuple
	c = db.cursor()
	c.execute('INSERT INTO memory (value) VALUES (?)',(string,))
	newkey = c.lastrowid
	if string in cache:
		cache[string].append(newkey)
	else:
		cache.update({string : [newkey]})

	return newkey

def InsertPhrase(memorytuple, wordlist, sync=True):
	db, cache = memorytuple
	i = 0
	if len(wordlist) != 0:
		for word in wordlist:
			if word != '':
				InsertMemory(memorytuple, word)
				i += 1
		if i > 0:
			InsertMemory(memorytuple, '')
	if sync == True:
		db.commit()
	
def CreateTermList(memorytuple):
	db, cache = memorytuple
	c = db.cursor()
	termlist = []
	for cur in cache['']:
		tempterm = ''
		termstart = cur - 1
		#go back 2 words before terminator
		if termstart >= 0:
			c.execute('SELECT value FROM memory WHERE id == (?)',(termstart,))
			term = c.fetchone()[0]
			if term != '':
				tempterm = term
				if (termstart - 1) > 0:
					c.execute('SELECT value FROM memory WHERE id == (?)',(termstart - 1,))
					term = c.fetchone()[0]
					if term != '':
						tempterm = term + ' ' + tempterm
		if tempterm != '':
			termlist.append(tempterm)
		
	return termlist

def CreateBuffer(memorytuple, termlist):
	bufferlist = []
	for i in range(0,BUFFSIZE):
		bufferlist.append(Response(memorytuple, termlist))
		
		sys.stdout.write("\r%d" %i) #DEBUG
		sys.stdout.flush() #DEBUG
	print 
		
	return bufferlist

def Terminator(buf, textend):
	if textend in buf:
		return True
	else:
		return False

def TryNext(dbcursor):
	queryresult = dbcursor.fetchone()
	if queryresult == None:
		return ''
	else:
		return queryresult[1]

def ReturnPattern(memorytuple, lastword):
	db, cache = memorytuple
	#check cache consistency
	assert lastword in cache
	randwordindex = random.choice(cache[lastword])
	c = db.cursor()
	c.execute('SELECT id, value FROM memory WHERE id > (?) LIMIT (?)',(randwordindex, 3))
	w1 = TryNext(c)
	w2 = TryNext(c)
	w3 = TryNext(c)
	return (w1, w2, w3)

def Response(memorytuple, termlist):
	#take a random terminator from memory and get the next 3 words
	w1, w2, w3 = ReturnPattern(memorytuple, '')
	if w2 == '':
		w3 = w1
		w2 = ''
		w1 = ''
	if w3 == '':
		w3 = w2
		w2 = w1
		w1 = ''
	tempresponse = w1 + ' ' + w2 + ' ' + w3
	dupresponsecount = 0
	oldresponse = ''
	while True:
		t1, t2, t3 = ReturnPattern(memorytuple, w3)
		partresponse = t1 + ' ' + t2 + ' ' + t3
		if oldresponse != '' and oldresponse == partresponse:
			dupresponsecount += 1
		oldresponse = partresponse
		tempresponse = tempresponse + ' ' + partresponse
		#print tempresponse
		if Terminator(termlist, t2 + ' ' + t3) or t3 == '' or dupresponsecount > MAXDUP:
			break
	if dupresponsecount > MAXDUP:
		return (tempresponse, False)
	else:
		return (tempresponse, True)

def Percent(memorytuple, word):
	db, cache = memorytuple
	word = word.lower()
	totallen = 0
	wordcount = 0
	cleanword = Text.Clean(word)

	if not word in cache and not cleanword in cache:
		return 0
	if word in cache:
		wordcount = len(cache[word])
	if cleanword in cache and cleanword != word:
		wordcount += len(cache[cleanword])

	for w in cache:
		if w != '':
			totallen += len(cache[w])
	result = (float(wordcount)/float(totallen))*100.0
	return int(round(result))

def LowestPercent(memorytuple, wordlist):
	lowestperc = 101
	for word in wordlist:
		wordperc = Percent(memorytuple, word)
		if wordperc < lowestperc:
			lowestperc = wordperc
	return lowestperc

def EraseList(lst):
	while True:
		try:
			lst.pop()
		except IndexError:
			break

def BestResponse(memorytuple, bufferlist, termlist, lastsubs, wordlist):
	db, cache = memorytuple
	totalsent = 0
	lowestperc = LowestPercent(memorytuple, wordlist)
	print "---" #DEBUG
	print "Keyword: ", 100-lowestperc, "%" #DEBUG
	print "Lastsubs: ", lastsubs #DEBUG
	keyword = []
	if lastsubs != []:
		for word in lastsubs:
			keyword.append(word)
	EraseList(lastsubs)
	for word in wordlist:
		if Percent(memorytuple, word) == lowestperc:
			lastsubs.append(word)
			keyword.append(word)
	
	print "Keywords: ", keyword #DEBUG
	
	if len(wordlist) == 0 and len(keyword) == 0:
		return Response(memorytuple, termlist)[0]
	
	start_time = time.clock()
	possiblelst = []
	created = 0
	matches = {}
	while True:
		while True:
			if totalsent > (BUFFSIZE - 1):
				possibletpl = Response(memorytuple, termlist)
			else:
				possibletpl = bufferlist[totalsent]
			
			possible = possibletpl[0]
			possisgood = possibletpl[1]
			totalsent += 1
			
			
			parseposs = Text.ParsePhrase(possible)
			count = 0
			for w in keyword:
				for pw in parseposs:
					if Text.Clean(w) == Text.Clean(pw):
						count += 1
			seconds = int(round(time.clock() - start_time))
			if count > 0 or seconds > TIMEFRAME:
				break
		
		possiblelst.append(possible)
		if possisgood == True:
			#if the sentence is good and not too long then match = exact count
			#else subtract 1 if len > 100, and then subtract 1 after every 40 more
			if len(possible) > 100:
				lengthscore = (len(possible) - 100)/40 + 1
				if count - lengthscore >= 0:
					matches[created] = count - lengthscore
				else:
					matches[created] = 0
			else:
				matches[created] = count
		else:
			#if a sentence is not good match = 0
			matches[created] = 0
		created += 1
		assert created == len(possiblelst)
		seconds = int(round(time.clock() - start_time))
		if created == POSSIBLEMAX or seconds > TIMEFRAME:
			break
	
	#calculate best match number
	maxmatched = 0
	for i in range(0, created):
		if matches[i] >= maxmatched:
			maxmatched = matches[i]
	#create a list of sentences with max number of matches	
	bestresplst = []
	for i in range(0, created):
		if matches[i] == maxmatched:
			bestresplst.append(possiblelst[i])
	
	bestresp = random.choice(bestresplst).rstrip(' ')
	
	print "Generated: ", totalsent #DEBUG
	for p in possiblelst: #DEBUG
		print "- ", p #DEBUG
	print "Matches: ", matches #DEBUG
	print "Best match no: ", maxmatched #DEBUG
	print "---" #DEBUG
	return bestresp

def Learn(memorytuple, text):
	cleantext = Text.AddPunct(text.lower())
	wordlist = Text.ParsePhrase(cleantext)
	InsertPhrase(memorytuple, wordlist)
	
def UpdateTermList(termlist, wordlist):
	tempterm = ''
	lastlist = wordlist[-2:]
	for word in lastlist:
		tempterm = tempterm + ' ' + word
	term = tempterm.lstrip()
	termlist.append(term)

def LearnAndUpdateTerm(memorytuple, termlist, text):
	cleantext = Text.AddPunct(text.lower())
	wordlist = Text.ParsePhrase(cleantext)
	InsertPhrase(memorytuple, wordlist)
	UpdateTermList(termlist, wordlist)



if __name__ == '__main__':

	memory = OpenMemory(sys.argv[1])
	mem, cache = memory
	
	lastsubs = []
	termlst = CreateTermList(memory)
	bufferlst = CreateBuffer(memory, termlst)
	
	try:
		while True:
			p = Text.AddPunct(raw_input("~$ "))
			wordlst = Text.ParsePhrase(p.lower())
			print "------------------------------"
			res = BestResponse(memory, bufferlst, termlst, lastsubs, wordlst).strip()
			res2 = res[0].upper() + res[1:]
			print res2
	except (KeyboardInterrupt, SystemExit, EOFError):
		print "Saving..."
		CloseMemory(memory, sys.argv[1])
