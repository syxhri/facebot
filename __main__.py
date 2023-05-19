import random, sys, os, postify, requests, secrets, string, json
from flask import Flask, request
from pymessenger.bot import Bot
from ping3 import ping as ping3
from openai import GPT, DALL_E
from utils import JSON

cwd = os.getcwd()

if len(sys.argv) > 1 and sys.argv[1].isdigit():
	PORT = int(sys.argv[1])
else:
	PORT = 4000

def uid(length=12):
	alphanum = string.ascii_letters + string.digits
	generated = ''
	for i in range(length):
		generated += secrets.choice(alphanum)
	return generated

def simi(text, lang='id'):
	result = postify.post(
		url = 'https://api.simsimi.vn/v1/simtalk',
		data = {
			'text': text,
			'lc': lang.lower()
		}
	).json
	return result.get('message')

app = Flask(__name__)
ACCESS_TOKEN = 'EAAHqwCtV0QQBAJnIYlZA4UNWoBDqfZCQ55RCPHqEWDZB0KLEBpuyyqpxC34RUn3zp2FkaPZCXGIfLPsUr3A8PFHIAo0bH5n6tZByNQ5OYqMzlTYkuVoxEZC64rYxyGR3Fb7zGWRqa3PZBLcHRcTdoRUJta2Vbi398jV5mb4ZBR9sCwbvdVfOdxsi'
VERIFY_TOKEN = 'alipyu'
bot = Bot(ACCESS_TOKEN)
setting = JSON()
setting.parse(open(cwd + '/setting.json', 'r').read())
prefix = setting.prefix
commands = setting.prefix
aikey = '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'
aid = uid()
sid = None
defset = {}

def ping(host='www.google.com'):
	time = ping3(host)
	time *= 1000
	time = '{:.1f} ms'.format(time)
	return time

@app.route("/", methods=['GET', 'POST'])
def receive_message():
	if request.method == 'GET':
		token_sent = request.args.get("hub.verify_token")
		return verify_fb_token(token_sent)
	else:
		output = request.get_json()
		process(output, debug=True)
		return "Message Processed"

def process(output, debug=False):
	global sid
	for event in output['entry']:
		messaging = event['messaging']
		for message in messaging:
			if message.get('message'):
				if debug:
					print('\n', message, '\n')
				rid = message['sender']['id']
				proses_db(rid)
				proses(rid, message['message'])

def proses(rid, message):
	text = message.get('text') or ''
	text = text.strip()
	media = None
	if message.get('attachments'):
		img_url = message['attachments'][0]['payload']['url']
		path = sid + '/images/' + img_url.split('/')[5].split('?')[0]
		open(path, 'wb').write(postify.get(img_url).binary)
		media = {
			'url': img_url,
			'path': path
		}
	reply(rid, text, media)

def reply(rid, text, media=None):
	global aikey
	global defset
	aikey = defset.get('aikey') or aikey
	if text.startswith('/') or text.startswith('!') or text.startswith('.'):
		prefa = text[0]
		args = text.split()
		cmd = args[0][1:].strip()
		if defset.get('enablecmd') == False and cmd != 'cmd':
			send(rid, 'Commands not enabled. Enable commands using !cmd on')
			return
		if (cmd == 'cgpt' or cmd == 'chatgpt') and len(args) > 1:
			gpt = GPT(aikey, aid)
			prompt = text.replace(prefa + cmd, '').strip()
			gpt.chat(prompt)
			send(rid, gpt.response)
		elif cmd == 'ping':
			if len(args) > 1:
				send(rid, ping(host=args[1]))
			else:
				send(rid, ping())
		elif cmd == 'autoreply' and len(args) > 1:
			if args[1] == 'on':
				defset['autoreply'] = True
				defset['autoreplyai'] = False
				defset['echotext'] = False
				send(rid, 'Auto reply ON')
			elif args[1] == 'off':
				defset['autoreply'] = False
				send(rid, 'Auto reply OFF')
			else:
				send(rid, 'Unknown option "{}". Only "on" and "off" allowed').format(args[1])
			open(sid + '/setting.json', 'w').write(json.dumps(defset))
		elif cmd == 'autoreplyai' and len(args) > 1:
			if args[1] == 'on':
				defset['autoreplyai'] = True
				defset['autoreply'] = False
				defset['echotext'] = False
				send(rid, 'Auto reply by AI ON')
			elif args[1] == 'off':
				defset['autoreplyai'] = False
				send(rid, 'Auto reply by AI OFF')
			else:
				send(rid, 'Unknown option "{}". Only "on" and "off" allowed').format(args[1])
			open(sid + '/setting.json', 'w').write(json.dumps(defset))
		elif cmd == 'echotext' and len(args) > 1:
			if args[1] == 'on':
				defset['echotext'] = True
				defset['autoreply'] = False
				defset['autoreplyai'] = False
				send(rid, 'Echo text ON')
			elif args[1] == 'off':
				defset['echotext'] = False
				send(rid, 'Echo text OFF')
			else:
				send(rid, 'Unknown option "{}". Only "on" and "off" allowed').format(args[1])
			open(sid + '/setting.json', 'w').write(json.dumps(defset))
		elif cmd == 'echoimg' and len(args) > 1:
			if args[1] == 'on':
				defset['echoimg'] = True
				send(rid, 'Echo image ON')
			elif args[1] == 'off':
				defset['echoimg'] = False
				send(rid, 'Echo image OFF')
			else:
				send(rid, 'Unknown option "{}". Only "on" and "off" allowed').format(args[1])
			open(sid + '/setting.json', 'w').write(json.dumps(defset))
		elif cmd == 'cmd' and len(args) > 1:
			if args[1] == 'on':
				defset['enablecmd'] = True
				send(rid, 'Commands enabled')
			elif args[1] == 'off':
				defset['enablecmd'] = False
				send(rid, 'Commands disabled')
			else:
				send(rid, 'Unknown option "{}". Only "on" and "off" allowed').format(args[1])
			open(sid + '/setting.json', 'w').write(json.dumps(defset))
		elif cmd == 'aikey' and len(args) > 1:
			defset['aikey'] = args[1]
			send(rid, 'OpenAI api key changed')
			open(sid + '/setting.json', 'w').write(json.dumps(defset))
		else:
			send(rid, 'Unknown command or option')
	else:
		isechotext = defset.get('echotext') == True
		isautoreply = not isechotext and defset.get('autoreply') == True and defset.get('autoreplyai') == False
		isautoreplyai = not isechotext and not isautoreply and defset.get('autoreplyai')
		isechoimg = defset.get('echoimg')
		if isechoimg and media.get('url'):
			sendiu(rid, media['url'])
		if isautoreply:
			send(rid, simi(text))
		if isautoreplyai:
			gpt = GPT(aikey, aid)
			gpt.chat(text)
			send(rid, gpt.response)
		if isechotext:
			send(rid, text)

def proses_db(rid):
	global sid
	global defset
	if sid is None:
		sid = str(rid)
	if not os.path.exists(sid):
		os.mkdir(sid)
	if not os.path.exists(sid + '/images'):
		os.mkdir(sid + '/images')
	if not os.path.exists(sid + '/audio'):
		os.mkdir(sid + '/audio')
	if not os.path.exists(sid + '/videos'):
		os.mkdir(sid + '/videos')
	if not os.path.exists(sid + '/docs'):
		os.mkdir(sid + '/docs')
	if not os.path.exists(sid + '/db'):
		os.mkdir(sid + '/db')
	if not os.path.exists(sid + '/setting.json'):
		defset = {
			'autoreply': False,
			'autoreplyai': False,
			'echotext': True,
			'enablecmd': True,
			'echoimg': False,
			'aikey': aikey
		}
		open(sid + '/setting.json', 'w').write(json.dumps(defset))
	else:
		defset = json.load(open(sid + '/setting.json'))

def verify_fb_token(token_sent):
	if token_sent == VERIFY_TOKEN:
		return request.args.get("hub.challenge")
	return 'Invalid verification token'

def get_message():
	sample_responses = ["Kamu menakjubkan!", "Aku ingin memilikimu", "...", "Apa?"]
	return random.choice(sample_responses)

def send(rid, reply):
	bot.send_text_message(rid, reply)
	return "success"

def sendi(rid, img_path):
	bot.send_image_url(rid, img_path)
	return "success"

def sendiu(rid, img_url):
	bot.send_image_url(rid, img_url)
	return "success"

if __name__ == "__main__":
	app.run(port=PORT)
