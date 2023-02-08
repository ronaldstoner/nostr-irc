#!/usr/bin/env python3
#
# Project:      nostr deleted events parser
# Members:      ronaldstoner
#
version = "0.0.1"

import asyncio
import datetime
import json
import time
import websockets
from colorama import Fore, Back, Style

search_days = 1                   # How many days of events to query from relay

async def subscribe_to_notes(uri, time_since):
    async with websockets.connect(uri) as websocket:
        search_filter = {
            "kinds": [1],
            "since": time_since,
            "until": int(time.time())
        }
        #TODO: Randomize an end identifier for unique sub id i.e. nostr-irc-a6s8s23
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
                    print(Style.BRIGHT + f"[{local_timestamp}] " + 
                          Style.NORMAL + "<" + 
                          Fore.GREEN + f"{pubkey}" +
                          Fore.WHITE + ">: " +
                          Style.NORMAL + f"{event_content}")
                    last_event_time = event_time
            else:
                # Resub to new messages from relay
                # TODO: Fix this retry logic to connect
                #       Maybe use socket pools?
                time_since = last_event_time if last_event_time is not None else int(time.time())
                search_filter = {
                    "kinds": [1],
                    "since": time_since,
                    "until": int(time.time())
                }
                await websocket.send(json.dumps(["REQ", "nostr-irc", search_filter]))

async def update_status_bar(relay):
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_bar = Back.WHITE + Fore.BLACK + f"Connected to: {relay}" + " " * (60 - len(relay)) + f"Nostr IRC {current_time}"
        print(f"\033[1;0H{status_bar}" + Back.BLACK + Fore.WHITE)
        await asyncio.sleep(1)

async def main():
    # Clear console
    print("\033c")
    relays = [
        "wss://relay.stoner.com" 
        ]
    time_since = int(time.mktime((datetime.datetime.now() - datetime.timedelta(days=search_days)).timetuple()))
    tasks = [subscribe_to_notes(relay, time_since) for relay in relays]
    status_bar_task = update_status_bar(relays[0])
    tasks.append(status_bar_task)
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
