import sys
import Memory
import Text
import re

botname = sys.argv[1]
txtpath = sys.argv[2]
newlineend = re.compile('\n$')

txtfile = open(txtpath)
memory = Memory.OpenMemory(botname)
i = 0

for line in txtfile:
	if i < 2:
		i += 1
		continue
	text = line.replace('"','').lower().strip()
	if line.startswith('***'):
		Memory.InsertMemory(memory, '')
	else:
		cleantext = newlineend.sub('', text).replace('\\r','').replace('\\n','').replace('\n','').replace('\\','').decode("utf-8")
		Memory.InsertMemory(memory, cleantext)

Memory.CloseMemory(memory, botname)
txtfile.close()
