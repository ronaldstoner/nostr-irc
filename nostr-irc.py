#!/usr/bin/env python3
#
# Project:      nostr-irc
# Members:      ronaldstoner
#
version = "0.0.3"

import asyncio, curses, datetime, json, time, websockets, uuid
#from nip05 import get_nip05

#search_days = 1
scroll_index = 0
scroll_buffer = 5000
client_uuid = uuid.uuid1()
ping_keepalive = 30        # Ping keep alive time
ping_timeout = 10 
nip_05_resolution = True

def load_event_filters():
    try:
        event_filter_list = []
        with open("event.filters", "r") as file:
            for line in file:
                line = line.strip()
                event_filter_list.append(line)
                #print(str(event_filter_list))
    except Exception as e:
        print("Could not load event filter list - ", e)
    return event_filter_list

def load_pubkey_filters():
    try:
        pubkey_filter_list = []
        with open("pubkey.filters", "r") as file:
            for line in file:
                line = line.strip()
                pubkey_filter_list.append(line)
    except Exception as e:
        print("Could not load pubkey filter list - ", e)
    return pubkey_filter_list

def run_curses(stdscr):
    global status_bar
    global messages
    global input_line
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

async def get_nip05(pubkey, uri):
    search_filter_nip05 = {
        "kinds": [0],
        "authors": [pubkey]
    }

    try:
        async with websockets.connect(uri) as websocket_metadata:
            request = json.dumps(["REQ", "irc-nip05-" + pubkey[:8], search_filter_nip05])
            #messages.addstr(str("Request: " + request))

            await websocket_metadata.send(request)
            pubkey_metadata_reply = await websocket_metadata.recv()
            #messages.addstr(str("\n Reply: " + pubkey_metadata_reply))
            
            if "EOSE" not in pubkey_metadata_reply and pubkey_metadata_reply is not None:
                # Remove newline characters from the metadata string
                pubkey_metadata_reply = pubkey_metadata_reply.replace('\n', '')
                # Parse the JSON string
                pubkey_metadata = json.loads(pubkey_metadata_reply)
                #messages.addstr(str(f"\nMETADATA: { str(pubkey_metadata[2]['content']) }"))

                json_acceptable_string = pubkey_metadata[2]['content']
                d = json.loads(json_acceptable_string)
                name = d['name']
                #messages.addstr(str(f"Name: {name}"))

                nip_05_identifier = name
                nip_05_identifiers[pubkey] = nip_05_identifier

                await websocket_metadata.send(json.dumps(["CLOSE", "irc-nip05-" + pubkey[:8]]))
                pubkey_metadata_close = await websocket_metadata.recv()
                #messages.addstr(str("\n Reply: " + pubkey_metadata_close))
            else:
                nip_05_identifier = pubkey
                await websocket_metadata.send(json.dumps(["CLOSE", "irc-nip05-" + pubkey[:8]]))
                pubkey_metadata_close = await websocket_metadata.recv()
                #messages.addstr(str("\n Reply: " + pubkey_metadata_close))
    except Exception as e:
        nip_05_identifier = pubkey
        #messages.addstr(str(f"EXCEPTION!!! {e}"))

    pubkey_metadata_close = None
    pubkey_metadata_reply = None
    pubkey_metadata = None
    name = None
    request = None

    return nip_05_identifier

async def subscribe_to_notes(uri, time_since, messages, client_uuid):
    global scroll_index
    global nip_05_identifier
    event_filter_list = load_event_filters()
    pubkey_filter_list = load_pubkey_filters()
    while True:
        try:
            async with websockets.connect(uri, ping_interval=ping_keepalive, ping_timeout=ping_timeout) as websocket_notes:
                async def keepalive():
                    while True:
                        await websocket_notes.ping()
                        await asyncio.sleep(ping_keepalive)

                keepalive_task = asyncio.create_task(keepalive())

                search_filter = {
                    "kinds": [1],
                    "since": time_since
                }
                await websocket_notes.send(json.dumps(["REQ", "irc-" + str(client_uuid), search_filter]))
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

                            if nip_05_identifier is None and nip_05_resolution is True:

                                # Wait for a future websocket response
                                future = asyncio.ensure_future(get_nip05(pubkey, uri))

                                # Wait for the result of the Future
                                try:
                                    result = await asyncio.wait_for(future, timeout=2)
                                    if result is not None:
                                        nip_05_identifier = result
                                        color_pair = 4
                                    else:
                                        nip_05_identifier = pubkey[:8]
                                        color_pair = 3
                                except Exception as e:
                                    nip_05_identifier = pubkey[:8]
                                    color_pair = 3
                                    #messages.addstr(str(f"EXCEPTION! {e}\n"))
                            else:
                                if nip_05_identifiers[pubkey] == pubkey[:8]:
                                    color_pair = 3
                                else:
                                    color_pair = 4

                            nip_05_identifiers[pubkey] = nip_05_identifier

                            messages.addstr(f"[{local_timestamp}] ", curses.color_pair(1) | curses.COLOR_WHITE | curses.A_BOLD)
                            messages.addstr(f"<{nip_05_identifier}>: ", curses.color_pair(color_pair) | curses.A_BOLD)
                            messages.addstr(str(event_content) + "\n")
                            messages.refresh()
                            
                            last_event_time = event_time
                            reply = None
                            result = None
                            message = None
                            pubkey = None
                            event_content = None
                            event_time = None
                            nip_05_identifier = None      
 
        except websockets.exceptions.ConnectionClosedError as e:
            # handle the exception
            messages.addstr(f"Error: {e}")
            # perform any necessary cleanup or recovery actions
            # for example, attempt to reconnect to the websocket
            asyncio.run(main_task(relay, status_bar, time_since, messages, client_uuid))

async def update_status_bar(relay, status_bar):
    while True:
        status_bar.clear()
        y, x = status_bar.getmaxyx()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        status_bar.addstr(0, 0, f"{relay}")
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
    time_since = int(time.time()) #- (60 * 60 * 24 * search_days)
    #relay = "wss://relay.stoner.com"
    relay = "wss://relay.damus.io"
    asyncio.run(main_task(relay, status_bar, time_since, messages, client_uuid))

if __name__ == "__main__":
    curses.wrapper(main)