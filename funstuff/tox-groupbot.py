import sys
sys.path.append('../sqlite')
from Memory import *
from Text import *

import sys
import string
import re

from tox import Tox

from time import sleep
from os.path import exists

SERVER = ["54.199.139.199", 33445, "7F9C31FE850E97CEFD4C4591DF93FC757C7C12549DDD55F8EEAECC34FE76C029"]
GROUP_BOT = 'DF157E229E5A6446E58F30F7281D69E0A9F952DA644D5A86DC7D16DE35B5395FADBFE61A87AA'

NAME = "Daisy"

LNAME = NAME.lower()
class DaisyBot(Tox):
	def __init__(self):
		if exists('data'):
			self.load_from_file('data')

		self.memory = OpenMemory(LNAME)
		self.lastsubs = []
		self.termlst = CreateTermList(self.memory)
		self.bufferlst = CreateBuffer(self.memory, self.termlst)
		
		self.connect()
		self.set_name(NAME)
		self.set_status_message("")
		self.sent = None
		print('ID: %s' % self.get_address())

		self.tox_group_id = None

	def connect(self):
		print('connecting...')
		self.bootstrap_from_address(SERVER[0], 1, SERVER[1], SERVER[2])

	def ensure_exe(self, func, args):
		count = 0
		THRESHOLD = 50

		while True:
			try:
				return func(*args)
			except:
				assert count < THRESHOLD
				count += 1
				for i in range(10):
					self.do()
					sleep(0.02)

	def loop(self):
		checked = False
		self.joined = False
		self.request = False

		try:
			while True:
				status = self.isconnected()
				if not checked and status:
					print('Connected to DHT.')
					checked = True
					try:
						self.bid = self.get_friend_id(GROUP_BOT)
					except:
						self.ensure_exe(self.add_friend, (GROUP_BOT, "Hi"))
						self.bid = self.get_friend_id(GROUP_BOT)

				if checked and not status:
					print('Disconnected from DHT.')
					self.connect()
					checked = False

				self.do()
		except (KeyboardInterrupt, SystemExit, EOFError):
			self.save_to_file('data')
			CloseMemory(self.memory, LNAME)

	def on_connection_status(self, friendId, status):
		if not self.request and not self.joined \
				and friendId == self.bid and status:
			print('Groupbot online, trying to join group chat.')
			self.request = True
			self.ensure_exe(self.send_message, (self.bid, 'invite'))

	def on_group_invite(self, friendid, pk):
		if not self.joined:
			self.joined = True
			self.tox_group_id = self.join_groupchat(friendid, pk)
			print('Joined groupchat.')

	def on_group_message(self, groupnumber, friendgroupnumber, message):
		if message == self.sent:
			return
		name = self.group_peername(groupnumber, friendgroupnumber)
		print('TOX> %s: %s' % (name, message))
		p = Text.AddPunct(message.lstrip('^!').strip())
		if message.startswith("^" + LNAME) or message.startswith("!" + LNAME):
			if self.tox_group_id != None:
				wordlst = Text.ParsePhrase(p.lower())
				msg = BestResponse(self.memory, self.bufferlst, self.termlst, self.lastsubs, wordlst).strip()
				self.ensure_exe(self.group_message_send, (self.tox_group_id, msg))
				self.sent = msg
				print('%s> %s: %s' % (NAME, name, message))
		LearnAndUpdateTerm(self.memory, self.termlst, p)

t = DaisyBot()
t.loop()
