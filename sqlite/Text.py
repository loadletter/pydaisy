import re

PUNCTREGEX = re.compile('[!\(\)\\\/:;",\.\?]')

def ParsePhrase(string, botname='', username=''):
	if botname == '' or username == '':
		pass
	else:
		name_pattern = re.compile(re.escape(username), re.IGNORECASE)
		string = name_pattern.sub(botname, string)
	wordlist = string.split()
	return wordlist

def AddPunct(string):
	slen = len(string)
	if slen != 0 and string[slen-1] not in ['!','.','?']:
		return string + '.'
	else:
		return string

def Clean(string):
	result = PUNCTREGEX.sub('',string)
	return result

