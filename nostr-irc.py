#!/usr/bin/env python3
#
# Project:      nostr deleted events parser
# Members:      ronaldstoner
#
version = "0.0.2"

import asyncio, curses, datetime, json, time, websockets, uuid
#from nip05 import get_nip05

#search_days = 1
scroll_index = 0
scroll_buffer = 5000
client_uuid = uuid.uuid1()
ping_keepalive = 10        # Ping keep alive time
pubkey_filter_list = ["11111"]
event_filter_list = ["damuspeaker", 
                    "damuspeak", 
                    "https://t.me/+5kN62jRibGw2Mjdl",
                    "https://redenvelope.eventimtoken.com.cn",
                    "https://t.me/baga233",
                    "https://t.me/Smartinu_1",
                    "https://t.me/S9Coin_cn",
                    "https://t.me/jianhuanghui",
                    "https://xdjz6.nl",
                    "https://bb38.top",
                    "https://t.me/chatgptzhcn",
                    "https://t.me/damus88",
                    "https://t.me/huang885888", 
                    "WeChat 群欢迎进群交流",
                    "http://bit.ly/3laIr3u",
                    "有意加v: dosoos",
                    "快去领🌈`b a o把",
                    "https://discord.com/invite/SusQJveN",
                    "https://t.me/kuangbiao666",
                    "https://lemonwallet.cn/#/",
                    "https://t.me/jinpaichadang001",
                    "https://t.me/anyecha",
                    "https://airdrop.eventimtoken.com.cn",
                    "https://t.me/chigualixing",
                    "https://nostr.build/i/nostr.build",
                    "https://bit.ly/3JGAYU7"
                    ]

def run_curses(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    status_bar = curses.newwin(1, curses.COLS, 0, 0)
    status_bar.bkgd(" ", curses.color_pair(2))
    status_bar.refresh()

    messages = curses.newwin(curses.LINES - 2, curses.COLS, 1, 0)
    messages.bkgd(" ", curses.color_pair(1))
    messages.scrollok(True)
    messages.refresh()

    input_line = curses.newwin(1, curses.COLS, curses.LINES - 1, 0)
    input_line.bkgd(" ", curses.color_pair(1))
    input_line.refresh()
    return status_bar, messages, input_line

nip_05_identifiers = {} 

async def subscribe_to_notes(uri, time_since, messages, client_uuid):
    global scroll_index
    while True:
        try:
            async with websockets.connect(uri) as websocket_notes:
                search_filter = {
                    "kinds": [1],
                    "since": time_since
                    # "until": int(time.time())
                }
                await websocket_notes.send(json.dumps(["REQ", "nostr-irc-" + str(client_uuid), search_filter]))
                last_event_time = None
                while True:
                    reply = await websocket_notes.recv()
                    message = json.loads(reply)
                    if "EOSE" not in message:
                        local_timestamp = datetime.datetime.fromtimestamp(message[2]["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
                        pubkey = message[2]["pubkey"]
                        event_content = message[2]["content"]
                        event_time = message[2]["created_at"]
                        if pubkey not in pubkey_filter_list and not any(f in event_content for f in event_filter_list):

                            nip_05_identifier = nip_05_identifiers.get(pubkey)

                            #messages.addstr(f"\n ! NIP05 Lookup: pub: {pubkey}  name: {nip_05_identifier}")

                            if nip_05_identifier is None:
                                async with websockets.connect(uri) as websocket_metadata:
                                    search_filter = {
                                        "kinds": [0],
                                        "authors": [pubkey]
                                    }
                                    request = json.dumps(["REQ", "nostr-irc-nip05" + pubkey, search_filter])
                                    #messages.addstr(str("Request: " + request))

                                    await websocket_metadata.send(request)
                                    pubkey_metadata_reply = await websocket_metadata.recv()
                                    #messages.addstr(str("\n Reply: " + pubkey_metadata_reply))

                                    await websocket_metadata.send(json.dumps(["CLOSE", "nostr-irc-nip05" + pubkey]))
                                    pubkey_metadata_close = await websocket_metadata.recv()
                                    #messages.addstr(str("\n Reply: " + pubkey_metadata_close))
                                    
                                    pubkey_metadata = json.loads(pubkey_metadata_reply)

                                    try:
                                        name_metadata = str(pubkey_metadata[2]['content'])
                                        json_acceptable_string = name_metadata.replace("'", "\"")
                                        d = json.loads(json_acceptable_string)
                                        name = d['name']

                                        nip_05_identifier = name
                                        nip_05_identifiers[pubkey] = nip_05_identifier
                                    except:
                                        nip_05_identifier = pubkey[-8:]

                            #messages.addstr(f"[{local_timestamp}] {display_identifier}: {event_content}\n")
                            messages.addstr(f"[{local_timestamp}] ", curses.color_pair(1) | curses.COLOR_WHITE | curses.A_BOLD)

                            #messages.addstr(f" <{display_identifier}>: ")
                            messages.addstr(f"<{nip_05_identifier}>: ", curses.color_pair(3) | curses.A_BOLD)

                            #event_content = f": {event_content}"
                            messages.addstr(str(event_content) + "\n")

                            messages.refresh()
                            last_event_time = event_time
                            pubkey_metadata_reply = ""

                    # else:
                    #     time_since = last_event_time if last_event_time is not None else int(time.time())
                    #     search_filter = {
                    #         "kinds": [1],
                    #         "since": time_since,
                    #         "until": int(time.time())
                    #     }
                    #     await websocket_notes.send(json.dumps(["REQ", "nostr-irc", search_filter]))
        except asyncio.TimeoutError:
            async with websockets.connect(uri, ping_interval=ping_keepalive) as websocket_notes:
                search_filter = {
                    "kinds": [1],
                    "since": time_since
                    # "until": int(time.time())
                }
                await websocket_notes.send(json.dumps(["REQ", "nostr-irc-" + str(client_uuid), search_filter]))
                break

async def update_status_bar(relay, status_bar):
    while True:
        status_bar.clear()
        y, x = status_bar.getmaxyx()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        status_bar.addstr(0, 0, f"Connected to: {relay}")
        status_bar.addstr(0, x//2-len("nostr-irc")//2, "nostr-irc")
        status_bar.addstr(0, x-len(timestamp)-1, timestamp)
        status_bar.refresh()
        await asyncio.sleep(1)

async def main_task(relay, status_bar, time_since, messages, client_uuid):
    tasks = [
        asyncio.create_task(update_status_bar(relay, status_bar)),
        asyncio.create_task(subscribe_to_notes(relay, time_since, messages, client_uuid)),
    ]
    await asyncio.gather(*tasks)

def main(stdscr):
    status_bar, messages, input_line = run_curses(stdscr)
    time_since = int(time.time()) # - (60 * 60 * 24 * search_days)
    #relay = "wss://relay.stoner.com"
    relay = "wss://relay.damus.io"
    asyncio.run(main_task(relay, status_bar, time_since, messages, client_uuid))

if __name__ == "__main__":
    curses.wrapper(main)
