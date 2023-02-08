#!/usr/bin/env python3
#
# Project:      nostr deleted events parser
# Members:      ronaldstoner
#
version = "0.0.2"

import asyncio, curses, datetime, json, time, websockets

search_days = 1
nip_05_identifiers = []

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

async def subscribe_to_notes(uri, time_since, messages):
    async with websockets.connect(uri) as websocket:
        search_filter = {
            "kinds": [1],
            "since": time_since,
            "until": int(time.time())
        }
        await websocket.send(json.dumps(["REQ", "nostr-irc", search_filter]))
        last_event_time = None
        while True:
            reply = await websocket.recv()
            message = json.loads(reply)
            if "EOSE" not in message:
                local_timestamp = datetime.datetime.fromtimestamp(message[2]["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
                pubkey = message[2]["pubkey"][-8:]
                event_content = message[2]["content"]
                event_time = message[2]["created_at"]
                if last_event_time is None or event_time > last_event_time:
                    if pubkey not in nip_05_identifiers:
                        # NIP-05 lookup for new pubkeys
                        # Replace this with your NIP-05 name lookup code
                        pair_value = 4
                        nip_05_identifier = "Some NIP-05 Identifier" 
                        nip_05_identifiers.append(pubkey)
                    else:
                        pair_value = 3
                        nip_05_identifier = ""

                    timestamp = f"[{local_timestamp}] "
                    messages.addstr(str(timestamp), curses.color_pair(1) | curses.COLOR_WHITE | curses.A_BOLD)

                    display_identifier = f"<{nip_05_identifier}>" if nip_05_identifier else f"<{pubkey}>"
                    #pubkey = f"<{pubkey}>"
                    messages.addstr(str(display_identifier), curses.color_pair(pair_value) | curses.A_BOLD)

                    event_content = f": {event_content}"
                    messages.addstr(str(event_content) + "\n")
                    messages.refresh()
                    last_event_time = event_time
            else:
                time_since = last_event_time if last_event_time is not None else int(time.time())
                search_filter = {
                    "kinds": [1],
                    "since": time_since,
                    "until": int(time.time())
                }
                await websocket.send(json.dumps(["REQ", "nostr-irc", search_filter]))

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

async def main_task(relay, status_bar, time_since, messages):
    tasks = [
        asyncio.create_task(update_status_bar(relay, status_bar)),
        asyncio.create_task(subscribe_to_notes(relay, time_since, messages)),
    ]
    await asyncio.gather(*tasks)

def main(stdscr):
    status_bar, messages, input_line = run_curses(stdscr)
    time_since = int(time.time()) - (60 * 60 * 24 * search_days)
    relay = "wss://relay.stoner.com"
    asyncio.run(main_task(relay, status_bar, time_since, messages))

if __name__ == "__main__":
    curses.wrapper(main)