import sys
import Memory
import Text
import re

botname = sys.argv[1]
txtpath = sys.argv[2]
newlineend = re.compile('\n$')

txtfile = open(txtpath)
memory = Memory.OpenMemory(botname)
for line in txtfile:
	text = line.replace('"','').lower().strip()
	cleantext = Text.AddPunct(newlineend.sub('', text).replace('\\r','').replace('\\n','').replace('\n','').replace('\\','').decode("utf-8"))
	wordlist = Text.ParsePhrase(cleantext)
	Memory.InsertPhrase(memory, wordlist, False)

Memory.CloseMemory(memory, botname)
txtfile.close()
