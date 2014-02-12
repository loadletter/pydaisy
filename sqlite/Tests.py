import argparse, time
from Memory import *
from Text import *

BOTNAME="lel"
LEARN=False

def chatbot():
	memory = OpenMemory(BOTNAME)
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
			print res
			if LEARN == True:
				LearnAndUpdateTerm(memory, termlst, p)
	except (KeyboardInterrupt, SystemExit, EOFError):
		print "Saving..."
		CloseMemory(memory, BOTNAME)

def responsebenchmark():
	memory = OpenMemory(BOTNAME)
	termlst = CreateTermList(memory)
	start_time = time.clock()
	bufferlst = CreateBuffer(memory, termlst)
	for res in bufferlst:
		print repr(res)
	print "------------"
	print time.clock() - start_time
	print "------------"
	CloseMemory(memory, BOTNAME)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers()

	parser_a = subparsers.add_parser('chatbot', help='chatbot help')
	parser_a.set_defaults(func=chatbot)

	parser_b = subparsers.add_parser('respbenchmark', help='response speed help')
	parser_b.set_defaults(func=responsebenchmark)

	args = parser.parse_args()
	args.func()

