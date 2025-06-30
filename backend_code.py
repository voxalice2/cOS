# --- IMPORTANT ---

cOS = 982753087 # Internet Setup

cOS_version = 1.0 # <<<

unsafe_apps = "Unsafe1|Unsafe2"
























os_ids = []
os_conns = []
os_clients = []

import json
import scratchattach
import threading
import datetime

import os
import dotenv
dotenv.load_dotenv()

def valid_id(vid):
	if (vid > 964481547):
		allvars = scratchattach.get_cloud(vid)
		cOS_var = allvars.get_var('cOS')

		try:
			if (int(cOS_var or 0) > 214) and (int(cOS_var or 0) % 43 == 0): 
				return True
			else:
				return False
		except KeyError:
			return False
		except Exception as e:
			print(e)
			return False

	else:
		return False

def finish(out):
	print(out)
	return out

def os_connect(osid):

	if (valid_id(osid)):
		this_conn = session.connect_cloud(osid)
		this_client = this_conn.requests(used_cloud_vars=["1", "2", "3"])

		@this_client.event
		def on_ready():
			print(f"Client {osid} is ready")

		@this_client.event
		def on_request(request):
			print(f"{osid}: Request {request.request.name} made with args {request.arguments} at {request.timestamp}")

		@this_client.request
		def ver():
			print("Returning current version")
			return finish([str(cOS_version), str(unsafe_apps)])

		@this_client.request
		def news(x):
			n = int(x)
			with open('news.json') as nf:
				news = json.load(nf)
				if (n > -1):
					print(f"Article #{n} found")
					return finish(news['articles'][n]['content'])
				else:
					news_len = len(news['articles'])
					print(f"{news_len} articles found")

					return finish([news['articles'][-1]['name'], news['articles'][-2]['name'], news['articles'][-3]['name'], news['articles'][-4]['name'], news_len - 1])

		print(f"Launching client for {osid}")

		this_client.start()
	else:
		print(f'not connected :( {osid} is an invalid ID')

# --- IMPORTANT ---


def run():
	try:
		with open('banned.json', 'r') as bans_f:
			global bans
			bans = json.load(bans_f)

		with open('connected.json') as f:
			global connected
			connected = json.load(f)

		print(connected)

		global session
		session = scratchattach.login(os.getenv('scratch_user'), os.getenv('scratch_pass'))

		global cOS_connection
		global cOS_events
		cOS_connection = session.connect_cloud(cOS)
		cOS_events = cOS_connection.events()

		@cOS_events.event
		def on_set(event):
			event.user = str(cOS_connection.logs(filter_by_var_named="ID")[0].username)

			print(f"Setup: {event.user} set {event.var} to {event.value}")
			if (event.var == "ID") and (int(event.value) > 964481548):
				new_osid = int(event.value)
				if event.user in bans['banned']:
					cOS_connection.set_var("ID", 2)
					print(f"{event.user} is banned.")
				else:

					go_ahead = True
					for sublist in connected['connected']:
						if new_osid == sublist[0]:
							cOS_connection.set_var("ID", 1)
							print(f"{new_osid} is already connected!")
							go_ahead = False
							break

					if go_ahead:
						if (valid_id(new_osid)):
							connected['connected'].append([new_osid, event.user, datetime.datetime.utcnow().isoformat()])

							with open('connected.json', 'w') as f:
								print(connected)
								json.dump(connected, f, ensure_ascii=False)

							t = threading.Thread(target=os_connect, args=[new_osid])
							t.start()

							cOS_connection.set_var("ID", 1)
							print(f"{new_osid} is a valid cOS project ID")
						else:
							cOS_connection.set_var("ID", 0)
							print(f"{new_osid} is an invalid cOS project ID")

		@cOS_events.event
		def on_ready():
			print("cOS Internet Setup ready")

		for cid in connected['connected']:
			id = int(cid[0])
			print(id)
			t = threading.Thread(target=os_connect, args=[id])
			t.start()

		cOS_events.start(thread=True)
	except KeyboardInterrupt:
		pass