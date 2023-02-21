import asyncio, curses, datetime, json, re, time, websockets

from invoice import decode_lightning_invoice
from filters import load_event_filters, load_pubkey_filters
from nip02 import get_nip02_friends
from nip05 import get_nip05, nip_05_identifiers

# Assign initial values to the variables
lnd_amount = 0
lnd_description = None
nip_05_identifier = None
nip_05_identifiers = {}
nip_05_resolution = True
ping_keepalive = 30
ping_timeout = 10

# Subscribe to note kind=1 from now until forever
async def subscribe_to_notes(relay, status_bar, time_since, messages, client_uuid, friendlist):
    event_filter_list = load_event_filters()
    pubkey_filter_list = load_pubkey_filters()

    #messages.addstr(str(f"FRIENDLIST: {friendlist}"))

    while True:
        try:
            async with websockets.connect(relay, ping_interval=ping_keepalive, ping_timeout=ping_timeout) as websocket_notes:
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
                messages.addstr(f"\n * Connecting to {relay}...\n\n", curses.color_pair(1) | curses.A_DIM)

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
                        local_timestamp = datetime.datetime.fromtimestamp(message[2]["created_at"]).strftime("%H:%M:%S")
                        pubkey = message[2]["pubkey"]
                        event_content = message[2]["content"]
                        event_time = message[2]["created_at"]
                        # Event and pubkey filtering
                        if pubkey not in pubkey_filter_list and not any(f in event_content for f in event_filter_list):
                            nip_05_identifier = nip_05_identifiers.get(pubkey)

                            if nip_05_identifier is None and nip_05_resolution is True:
                                # Wait for a future websocket response
                                future = asyncio.ensure_future(get_nip05(pubkey, relay))

                                # Wait for the result of the Future
                                try:
                                    result = await asyncio.wait_for(future, timeout=3)

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

                            # Get NIP05 Name via Relay
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

                            # Replace new lines and line breaks with space so that event messages flow better
                            event_content = event_content.replace("\n", " ")

                            # This works - but we only want to enable it later for SDTVs and older CRTs
                            # Filter out emojis from event_content
                            # for char in event_content:
                            #     if ord(char) not in range(128):
                            #         # exclude non-ASCII characters - remove emojis
                            #         continue
                            #     filtered_content += char

                            # event_content = filtered_content

                            # Highlight friends/following
                            for item in friendlist:
                                if pubkey == item:
                                    color_pair = 5

                            # We have an event that is not blank, push it to message panel
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
            messages.addstr(f"\n * Connection Lost!\n * Reconnecting to {relay}...", curses.color_pair(1) | curses.A_DIM)
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
