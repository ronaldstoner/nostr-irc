#!/usr/bin/env python3
#
# Project:      nostr-irc
# Members:      ronaldstoner
#
version = "0.0.4"

import asyncio, curses, datetime, json, re, time, websockets, uuid

import ui
from filters import load_event_filters, load_pubkey_filters
from invoice import decode_lightning_invoice
from nip05 import get_nip05, nip_05_indentifiers
from updatetasks import update_status_bar, update_user_input

# Declare global variables
global client_uuid
global scroll_index
global nip_05_identifier
global nip_05_identifiers
global nip_05_resolution
global ping_keepalive
global ping_timeout
global lnd_amount
global lnd_description

# Assign initial values to the variables
client_uuid = uuid.uuid1()
ping_keepalive = 30
ping_timeout = 10
scroll_index = 0
nip_05_identifier = None
nip_05_identifiers = {}
nip_05_resolution = True
lnd_amount = 0
lnd_description = None

# TODO: Move to nip01.py module
async def subscribe_to_notes(uri, status_bar, time_since, messages, client_uuid):
    event_filter_list = load_event_filters()
    pubkey_filter_list = load_pubkey_filters()

    while True:
        try:
            async with websockets.connect(uri, ping_interval=ping_keepalive, ping_timeout=ping_timeout) as websocket_notes:
                async def keepalive():
                    try:
                        while True:
                            await websocket_notes.ping()
                            await asyncio.sleep(ping_keepalive)
                    except:
                        pass

                # Start the keepalive task
                keepalive_task = asyncio.create_task(keepalive())

                # Subscribe to websocket relay with search filter
                messages.addstr(f"\n * Connecting to {uri}...\n\n", curses.color_pair(1) | curses.A_DIM)

                search_filter = {
                    "kinds": [1],
                    "since": time_since
                }
                await websocket_notes.send(json.dumps(["REQ", "irc-" + str(client_uuid), search_filter]))

                while True:
                    reply = await websocket_notes.recv()
                    message = json.loads(reply)

                    # If the message is not End of Subscription and not blank
                    if "EOSE" not in message and message is not None:
                        local_timestamp = datetime.datetime.fromtimestamp(message[2]["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
                        pubkey = message[2]["pubkey"]
                        event_content = message[2]["content"]
                        event_time = message[2]["created_at"]
                        if pubkey not in pubkey_filter_list and not any(f in event_content for f in event_filter_list):
                            nip_05_identifier = nip_05_identifiers.get(pubkey)

                            if nip_05_identifier is None and nip_05_resolution is True:
                                # Wait for a future websocket response
                                future = asyncio.ensure_future(get_nip05(pubkey, uri))

                                # Wait for the result of the Future
                                try:
                                    result = await asyncio.wait_for(future, timeout=2)

                                    if result is not None:
                                        #messages.addstr(str("NIP05 RESULT" + result))
                                        nip_05_identifier = result
                                        color_pair = 4
                                    else:
                                        nip_05_identifier = pubkey[:8]
                                        color_pair = 3
                                except Exception as e:
                                    nip_05_identifier = pubkey[:8]
                                    color_pair = 3
                            else:
                                if nip_05_identifiers[pubkey] == pubkey[:8]:
                                    color_pair = 3
                                else:
                                    color_pair = 4

                            nip_05_identifiers[pubkey] = nip_05_identifier


                            # Lightning Invoice Parsing & Testing
                            test = re.compile('^.*lnbc.*$', re.MULTILINE)
                            test2 = re.compile('^.*lightning:lnbc.*$', re.MULTILINE)
                            if re.match(test, event_content) or re.match(test2, event_content):
                            #    lnd_amount, lnd_description = decode_lightning_invoice(event_content)
                            #    if lnd_amount:
                            #        event_content = f"[LIGHTNING INVOICE] Sats: {lnd_amount}  Reason: {lnd_description}"
                            #    else:
                            #        event_content = "[LIGHTNING INVOICE]"
                                event_content = "[LIGHTNING INVOICE]"


                            # This works - but we only want to enable it later for SDTVs and older CRTs
                            # Define a regular expression pattern to match emojis and newlines
                            #emoji_pattern = re.compile("[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001F1FF]|[\n]")
                            #filtered_content = ""
                            #for char in event_content:
                            #    if ord(char) not in range(128) and ord(char) != 10:
                            #        # exclude emojis and newlines
                            #            continue
                            #    filtered_content += char

                            # Filter out emojis and newlines from event_content
                            #event_content = emoji_pattern.sub("", filtered_content)

                            # We have an event that is not blank
                            if event_content and event_content != '' and event_content != ' ':
                                messages.addstr(f"[{local_timestamp}] ", curses.color_pair(1) | curses.COLOR_WHITE | curses.A_BOLD)
                                messages.addstr(f"<{nip_05_identifier}>: ", curses.color_pair(color_pair) | curses.A_BOLD)
                                messages.addstr(str(f"{event_content}\n"))
                                messages.refresh()

                            # Move the last event time forward and reset for next run
                            last_event_time = event_time
                            reply = None
                            result = None
                            message = None
                            pubkey = None
                            event_content = None
                            event_time = None
                            nip_05_identifier = None
                            lnd_amount = 0
                            lnd_description = None

        except websockets.exceptions.ConnectionClosedError as e:
            # Display an error message
            status_bar.erase()
            status_bar.addstr(0, 0, f"Websocket error: {str(e)}. Reconnecting...")
            status_bar.refresh()
            messages.addstr(f"\n * Connection Lost!\n * Reconnecting to {uri}...", curses.color_pair(1) | curses.A_DIM)
            messages.refresh()
            # Wait for some time before attempting to reconnect
            await asyncio.sleep(5)
            # Try to reconnect to the websocket
            continue

        except Exception as e:
            # Display an error message
            messages.addstr(str(f"Error: {str(e)}"))
            messages.refresh()
            break
            # Wait for some time before attempting to reconnect
            await asyncio.sleep(5)
            # Try to reconnect to the websocket
            continue

# asyncio task gather and handler
async def main_task(relay, status_bar, time_since, messages, client_uuid):
    tasks = [
        asyncio.create_task(update_status_bar(relay, status_bar)),
        asyncio.create_task(subscribe_to_notes(relay, status_bar, time_since, messages, client_uuid))
    ]
    await asyncio.gather(*tasks)

# main funciton call
def main(stdscr):
    ui_obj = ui.UI()
    status_bar, messages, input_title, input_line, input_box = ui_obj.run_curses(stdscr)
    time_since = int(time.time()) #- (60 * 60 * 24 * search_days)
    #relay = "wss://relay.stoner.com"
    #relay = "wss://relay.damus.io"
    relay = "wss://nos.lol"
    asyncio.run(main_task(relay, status_bar, time_since, messages, client_uuid))

# main curses wrapper
if __name__ == "__main__":
    curses.wrapper(main)
