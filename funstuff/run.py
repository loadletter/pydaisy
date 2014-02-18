#!/usr/bin/env python2
RATELIMIT=False
LEARN=True
ENABLEPROXY=True


if ENABLEPROXY == True:
	import socks
	import socket
	socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "localhost", 9150)
	socket.socket = socks.socksocket

from chatterbotapi import ChatterBotFactory, ChatterBotType

import sys
sys.path.append('../sqlite')
from Memory import *
from Text import *


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
			thinkstart = time.time()
			p = Text.AddPunct(msg)
			wordlst = Text.ParsePhrase(p.lower())
			msg = BestResponse(memory, bufferlst, termlst, lastsubs, wordlst).strip()
			out.flush()
			#maybe this could prevent bans from cleverbot
			if RATELIMIT == True:
				print "sleep",
				while (thinkstart + ((len(msg) + 1) / 15)) > time.time():
					time.sleep(1)
					print ".",
					sys.stdout.flush()
				print
			
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
		#bot1 = factory.create(ChatterBotType.PANDORABOTS, 'b0dafd24ee35a477')
		bot1 = factory.create(ChatterBotType.PANDORABOTS, '9fa364f2fe345a10') #mitsuku chatbot from mitsuku.com
		bot1session = bot1.create_session()
		bot1session.pandorabots_url = 'http://fiddle.pandorabots.com/pandora/talk-xml' #mitsuku doesn't work with the normal url
		chatbot(botname, bot1session, f)
	else:
		print "Invalid argument"
