# -*- coding: utf-8 -*-
import sys, sqlite3, zlib, html2text, re
import Memory
import nltk.data

COMPRESSED = True

botname = sys.argv[1]
dbpath = sys.argv[2]
post_reflink = re.compile("\[>>[0-9]+\]\([0-9]+\#p[0-9]+\)")
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
url_regex = re.compile(r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(‌​([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))""", re.DOTALL)
memory = Memory.OpenMemory(botname)

conn = sqlite3.connect(dbpath)
c = conn.cursor()
c.execute('SELECT com FROM posts')
result = c.fetchall()
for res in result:
	if res[0] == '':
		continue
	if COMPRESSED == True:
		raw = zlib.decompress(res[0])
		rawpost = raw.decode('utf-8')
	else:
		rawpost = res[0]
	post = html2text.html2text(rawpost)
	norefpost = post_reflink.sub('', post)
	nolinkpost = url_regex.sub('',norefpost)
	sentencelist = tokenizer.tokenize(nolinkpost)
	for sen in sentencelist:
		if not re.match(r'^\s*$', sen):
			clean = sen.replace('\n\n', '').replace('\n', ' ').lstrip(' ')
			tomem = clean.lower().split()
			Memory.InsertPhrase(memory, tomem, False)
c.close()
conn.close()
Memory.CloseMemory(memory, botname)
