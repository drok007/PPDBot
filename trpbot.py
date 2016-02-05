import reloader
reloader.enable(blacklist=['inspect','os','pickle','time','re','random','urllib','math','udquery','sys','traceback','json','hashlib','irc','irc.bot','irc.client','ircbot','bot','chatterbotapi','socket','collections'])


from irc import strings
from inspect import getmembers, isfunction
from bs4 import BeautifulSoup
import os,pickle,time,re,random,urllib2,urllib,urllib3,requests,math,udquery,sys,traceback,json,hashlib,socket,datetime,string
import certifi
import collections
import trpbot_commands
#import markovchain
#import stripclub
import redis
from irc.client import ip_numstr_to_quad,ip_quad_to_numstr
from pastebin import PastebinAPI
from irc import bot as ircbot
from fnmatch import fnmatch
from chatterbotapi import ChatterBotFactory, ChatterBotType
cbfactory = ChatterBotFactory()
cbot = cbfactory.create(ChatterBotType.CLEVERBOT)


HOST = 'b0rk.uk.quakenet.org' #'servercentral.il.us.quakenet.org' #irc.quakenet.org
PORT = 6667
NICK = 'nickname'
CHAN = '#nickname'
#trpbot_commands.AUTOJOIN = ['#purplepilldebate','#gotppd','#redpillwomen','#superior']
BOSS = 'drok'
VERSION = '#purplepilldebate bot, Gorilla Pi Version'
AUTH = 'AUTH authname password'
CONFIG = 'data/config.json'
keeptrying = True

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED', # Force certificate check.
    ca_certs=certifi.where(),  # Path to the Certifi bundle.
)

reply = 1
chain_length = 2
chattiness = 1
max_words = 30
BRAIN_FILE = 'data/brain_file.txt'
STOP_WORD = '\n'
markov = collections.defaultdict(list)

#requests.packages.urllib3.disable_warnings()

class PPDBot(ircbot.SingleServerIRCBot):
	def __init__(self,nickname=NICK,server=HOST,port=PORT,channel=CHAN):
		ircbot.SingleServerIRCBot.__init__(self,[(server, port)],nickname,nickname)
		self.reactor.add_global_handler('all_events',self.command_caller)
		self.cbot = cbot
		self.cbots = {}
		self.channel = channel
		self.build_commands()
		self.pick = pickle
		self.datetime = datetime
		self.tyme = time
		self.fnmatch = fnmatch
		self.version = VERSION
		self.re = re
		self.rng = random
		self.soop = BeautifulSoup
		self.url2 = urllib2
		self.url3 = urllib3
		self.boss = '%s.users.quakenet.org' % BOSS
		self.hashlib = hashlib
		self.mqueue = []
		self.urllib = urllib
		self.requests = requests
		#self.stripclub = stripclub
		self.udquery = udquery
		self.math = math
		self.os = os
		self.sys = sys
		self.json = json
		self.traceback = traceback
		self.botconfig = {}
		trpbot_commands.on_initialize(os.path.isfile,pickle,json,time)
                self.braining()
		self.reactor.execute_every(2.0,self.process_mqueue)
		self.load_config()
		self.pb = PastebinAPI()
		self.pbkey = None
		self.AUTOJOIN = trpbot_commands.AUTOJOIN
		self.socket = socket
		if 'pb_devkey' in self.botconfig and 'pb_username' in self.botconfig and 'pb_password' in self.botconfig and self.botconfig['pb_devkey'] and self.botconfig['pb_username'] and self.botconfig['pb_password']:
			self.pbkey = self.pb.generate_user_key(self.botconfig['pb_devkey'],self.botconfig['pb_username'],self.botconfig['pb_password'])
		#def execute_every(self, period, function, arguments=())

	
	def load_config(self):
		if os.path.isfile(CONFIG):
			with open(CONFIG) as f:
				self.botconfig = json.load(f)
		else:
			self.botconfig = {
				'pb_devkey':'',
				'pb_username':'',
				'pb_password':'',
				'irc_auth':'',
			}
			self.save_config()
			
        def braining(self):
            if os.path.isfile(BRAIN_FILE):
                f = open(BRAIN_FILE, 'r')
                for line in f:
                        add_to_brain(line, chain_length)
                uprint('Brain loaded!')
                f.close()
            else:
                uprint('Hoi! I need me some brains! Whaddya think I am, the Tin Man?')

	def save_config(self):
		with open(CONFIG,'wb') as f:
			self.json.dump(self.botconfig,f,sort_keys=True,indent=4)

	def process_mqueue(self):
		if not len(self.mqueue):
			return
		c,target,msg = self.mqueue.pop(0)
		uprint('PPDBot (in %s): %s' % (target,msg,))
		try:
			msg = ''.join(msg.splitlines())
			msg1 = '%s06%s%s' % (chr(3),msg[:386],chr(3))
			msg2 = ''
			if len(msg) > 386:
			    msg1 = '%s06%s%s' % (chr(3),msg[:386].rsplit(' ',1)[0],chr(3))
			    msg2 = msg[len(msg1)-3:]
			c.privmsg(target,msg1)
			if len(msg2):
				self.mqueue.append((c,target,msg2))
		except:
			#print('process_mqueue exception: %s' % (self.sys.exc_info(),))
			traceback.print_exc(file=sys.stdout)
			
	def add_mqueue(self,c,target,msg):
		self.mqueue.append((c,target,msg))
		
	def build_commands(self):
		self.commands = {}
		self.chatcmds = {}
		found = getmembers(trpbot_commands,isfunction)
		for fname,f in found:
			if len(fname) > 3 and fname[0:3] == 'on_':
				self.commands[fname] = f
			elif len(fname) > 4 and fname[0:4] == 'cmd_':
				self.chatcmds[fname] = f

	def command_caller(self,c,e):
		event_name = 'on_%s' % (e.type,)
		if event_name in self.commands:
			self.commands[event_name](self,c,e)
		#print('%s: %s' % (e.type,e.arguments[0] if len(e.arguments) else ''))


			
	def on_pubmsg(self,c,e):
		if e.target in self.channels:
			ch = self.channels[e.target]
			if self.boss in e.source and e.arguments[0] == '.reload':
				reloader.reload(trpbot_commands)
				self.build_commands()
				self.add_mqueue(c,e.target,'Reload complete.')
                        elif self.boss in e.source and e.arguments[0] =='.die':
                                raise KeyboardInterrupt('Die Command Received.')
		msg = e.arguments[0].strip()
                nick = e.source.nick
                mcmsg = ' '.join(e.arguments).encode('ascii','ignore')
                #uprint(mcmsg)
                if reply == '1':
                    if c.get_nickname() in mcmsg:
                        #time.sleep(0.2) #to prevent flooding
                        #mcmsg = re.compile(c.get_nickname() + '[:,]* ?', re.I).sub('', mcmsg)
                        prefix = '%s: ' % (nick, )
                    else:
                        prefix = '' 

                    add_to_brain(mcmsg, chain_length, write_to_file=True)
                    #uprint(mcmsg) #prints to stdout what sadface added to brain
                    if prefix or random.random() <= chattiness:
                        sentence = generate_sentence(mcmsg, chain_length, max_words)
                        if sentence:
                            self.add_mqueue(c,e.target,prefix + sentence)
                            #uprint(prefix + sentence) # ">" + "\t" + sentence #prints to stdout what sadface said
                # Replies to messages starting with the bot's name.
                elif reply == '2':
                    if mcmsg.startswith(c.get_nickname): #matches nickname, mecause of Noxz
                        #time.sleep(0.2) #to prevent flooding
                        #mcmsg = re.compile(c.get_nickname + "[:,]* ?", re.I).sub('', mcmsg)
                        prefix = "%s: " % (nick, )
                    else:
                        #mcmsg = re.compile(c.get_nickname + "[:,]* ?", re.I).sub('', mcmsg)
                        prefix = '' 

                    add_to_brain(mcmsg, chain_length, write_to_file=True)
                    #print "\t" + msg #prints to stdout what sadface added to brain
                    if prefix or random.random() <= chattiness:
                        sentence = generate_sentence(mcmsg, chain_length, max_words)
                        if sentence:
                            self.add_mqueue(c,e.target,prefix + sentence)
                            #uprint(prefix + sentence) #prints to stdout what sadface said
                else:     #for when you don't want it talking back
                    #print mcmsg
                    prefix = '' 
                    add_to_brain(mcmsg, chain_length, write_to_file=True)
                    if prefix or random.random() <= chattiness:
        #                sentence = generate_sentence(mcmsg, chain_length, max_words)
                        pass

	def on_nicknameinuse(self,c,e):
		c.nick('%s-' % (c.get_nickname(),))
		
	def on_welcome(self,c,e):
                uprint('Connected! Authing...')
		if AUTH or ('irc_auth' in self.botconfig and self.botconfig['irc_auth']):
			c.send_raw(AUTH if AUTH else self.botconfig['irc_auth'])
			c.mode(c.get_nickname(),'+x')
			uprint('Authed!')
		c.join(self.channel)
		for each_chan in trpbot_commands.AUTOJOIN:
			c.join(each_chan)
			self.add_mqueue(c,each_chan,'%s has arrived to touch your no no places.' % (c.get_nickname(),))
		
	def on_ctcp(self,c,e):
		nick = e.source.nick
		#uprint(' '.join(e.arguments))
		if e.arguments[0] == 'VERSION':
			c.ctcp_reply(nick,'VERSION %s' % (VERSION,))
		elif e.arguments[0] == 'PING':
                        if len(e.arguments) > 1:
                                #c.send_raw('PONG %s' % (e.arguments[1],))
                                c.ctcp_reply(nick,'PONG %s' % (e.arguments[1],))
                                uprint('PONG %s' % (e.arguments[1],))
                        else:
                                #c.send_raw('PONG')
                                c.ctcp_reply(nick,'PONG')
                                uprint('PONG')
		elif e.arguments[0] == 'DCC':
		        uprint('on_ctcp DCC: %s/%s/%s' % (e.arguments,e.target,e.source,))
		        msg = e.arguments[1]
		elif e.arguments[0] == 'DCC' and e.arguments[1].split(' ',1)[0] == 'CHAT':
			self.on_dccchat(c,e)
		        
	def on_dccchat(self,c,e):
		pass

        def on_disconnect(self,c,e):
                uprint('Disconnected.')
                if keeptrying == True:
                        uprint('Must reconnect. Reconnecting...')
                        bot.start()
                        
        def connected_checker(self):
            if not self.connection.is_connected() and keeptrying == True:
                uprint('Reconnecting...')
                bot.start()
                
def uprint(text):
	print(text.encode('UTF-8'))

def add_to_brain(msg, chain_length, write_to_file=False):
            #''.join(ch for ch in msg if ch.isalnum() or ch == ' ')
            msg = unicode(msg,'utf-8')
            msg.encode('utf-8',errors='ignore')
            if write_to_file:
                f = open(BRAIN_FILE, 'a')
                f.write(msg + '\n')
                f.close()
            buf = [STOP_WORD] * chain_length
            for word in msg.split():
                    markov[tuple(buf)].append(word)
                    del buf[0]
                    buf.append(word)
            markov[tuple(buf)].append(STOP_WORD)

def generate_sentence(msg, chain_length, max_words=100): #max_words is defined elsewhere
            if msg[-1][-1] in string.punctuation: 
        #        msg[-1] = msg[-1][:-1]
        #        msg.replace([-1], '')
        # converts string to list, drops the end character, converts back to string
                msg = list(msg)
                msg[-1] = msg[-1][:-1]
                msg[0] = msg[0].upper()
                msg = ' '.join(msg)
        #    buf = msg.split()[-chain_length:] 
            buf = msg.split()[:chain_length]   
        # If message is longer than chain_length, shorten the message.
            if len(msg.split()) > chain_length: 
                message = buf[:]
            else:
                message = []
                for i in xrange(chain_length):
                    message.append(random.choice(markov[random.choice(markov.keys())]))
            for i in xrange(max_words):
                try:
                    next_word = random.choice(markov[tuple(buf)])
                except IndexError:
                    continue
                if next_word == STOP_WORD:
                    break
                message.append(next_word)
                del buf[0] # What happpens if this is moved down a line?
                buf.append(next_word)
            return ' '.join(message)
        
if __name__ == '__main__':
	bot = PPDBot()
	while keeptrying:
		try:
			uprint('%s initialized. connecting...' % (VERSION,))
			bot.start()
		except UnicodeDecodeError:
			traceback.print_exc(file=sys.stdout)
		except KeyboardInterrupt:
			uprint('Disconnecting, KeyboardInterrupt')
			keeptrying = False
                        bot.disconnect(VERSION)
