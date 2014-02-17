from chatterbotapi import ChatterBotFactory, ChatterBotType

import sys
sys.path.append('../sqlite')
from Memory import *
from Text import *


LEARN=True

def chatbot(botname, remotebot, out=sys.stdout):
	memory = OpenMemory(botname)
	
	lastsubs = []
	termlst = CreateTermList(memory)
	bufferlst = CreateBuffer(memory, termlst)
	
	msg = "Hello!"
	out.write("BEGIN LOG: %s\n" % time.ctime())
	try:
		while True:
			out.write("Local: %s\n" % msg)
			msg = remotebot.think(msg)
			out.write("Remote: %s\n" % msg)
			p = Text.AddPunct(msg)
			wordlst = Text.ParsePhrase(p.lower())
			msg = BestResponse(memory, bufferlst, termlst, lastsubs, wordlst).strip()
			out.flush()
			if LEARN == True:
				LearnAndUpdateTerm(memory, termlst, p)
	except (KeyboardInterrupt, SystemExit, EOFError):
		print "Saving..."
		out.write("END LOG: %s\n" % time.ctime())
		out.close()
		CloseMemory(memory, botname)

if __name__ == '__main__':
	factory = ChatterBotFactory()
	if sys.argv[1] == "clever":
		botname = "daisy_vs_clever"
		f = open(botname + ".log", "a")
		bot1 = factory.create(ChatterBotType.CLEVERBOT)
		bot1session = bot1.create_session()
		chatbot(botname, bot1session, f)
	elif sys.argv[1] == "pandora":
		botname = "daisy_vs_pandora"
		f = open(botname + ".log", "a")
		bot1 = factory.create(ChatterBotType.PANDORABOTS, 'b0dafd24ee35a477')
		bot1session = bot1.create_session()
		chatbot(botname, bot1session, f)
	else:
		print "Invalid argument"
