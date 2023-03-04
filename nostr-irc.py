# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
# Project:      nostr-irc
# Members:      ronaldstoner
#
version = "0.0.4.3"

# Imports - packages
import argparse, asyncio, curses, secrets, secp256k1, time, uuid

# Imports - local
import ui
from nip01 import subscribe_to_notes
from nip02 import get_nip02_friends
from nip05 import get_nip05
from input import get_user_input
from updatetasks import update_status_bar

# Declare global variables
global client_uuid
global scroll_index
global nip_05_identifier
global nip_05_identifiers
global friendlist

friendlist = []
nip_05_identifiers = {}

# Assign initial values to the variables
client_uuid = uuid.uuid1()


# main function call
def main(stdscr):
    
    # Data gathering 
    time_since = int(time.time()) #- (60 * 60 * 24 * search_days)
    relay = args.relay if args.relay else "wss://nos.lol"

    # Load privkey from args, but if not generate a random key for chatting
    privkey = args.privatekey if args.privatekey is not None else secrets.token_bytes(32).hex()

    # Derive pubkey from privkey
    pk = secp256k1.PrivateKey(bytes.fromhex(privkey))
    publickey = pk.pubkey.serialize()[1:].hex()

    # Get friendlist from pubkey - but only if user is a specifying one
    if args.privatekey is not None:
        try:
            friendlist = asyncio.run(get_nip02_friends(relay, publickey))
        except Exception as e:
            print(e)
            friendlist = []
    else:
        friendlist = []

    # NIP05 - friendly name for input bar 
    try:
        nip_05_identifier = asyncio.run(get_nip05(publickey, relay))
    except:
        nip_05_identifier = None

    # Load the UI
    ui_obj = ui.UI()
    status_bar, messages, input_title, input_line, input_box = ui_obj.run_curses(stdscr, publickey, nip_05_identifier)

    # Call the main_task function with the friendlist
    try:
        asyncio.run(main_task(relay, status_bar, publickey, privkey, time_since, messages, input_box, client_uuid, friendlist))
    except asyncio.exceptions.CancelledError:
        pass    
    except KeyboardInterrupt:
        pass

# asyncio task gather and handler
async def main_task(relay, status_bar, publickey, privkey, time_since, messages, input_box, client_uuid, friendlist):



    tasks = [
        asyncio.create_task(update_status_bar(relay, status_bar)),
        asyncio.create_task(subscribe_to_notes(relay, status_bar, time_since, messages, client_uuid, friendlist)),
        asyncio.create_task(get_user_input(input_box, relay, privkey, messages, status_bar))
    ]

    try:
        # Run the tasks in the background
        await asyncio.gather(*tasks)

    except Exception as e:
        print(f"EXCEPTION: {e}")
        time.sleep(1000)    


# main curses wrapper
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="nostr-irc")
    parser.add_argument("-p", "--privatekey", help="The private key for signing messages in hex format")
    parser.add_argument("-r", "--relay", help="The secure websocket relay to use (e.g. wss://nos.lol)")

    args = parser.parse_args()
    curses.wrapper(main)
