#!/usr/bin/env python3
#
# Project:      nostr-irc
# Members:      ronaldstoner
#
version = "0.0.4.2"

# Imports - packages
import argparse, asyncio, curses, secrets, time, uuid

# Imports - local
import ui
from nip01 import subscribe_to_notes
from nip02 import get_nip02_friends
from input import get_user_input
from updatetasks import update_status_bar

# Declare global variables
global client_uuid
global scroll_index
global nip_05_identifier
global nip_05_identifiers
global nip_05_resolution
global friendlist

friendlist = []

# Assign initial values to the variables
client_uuid = uuid.uuid1()


# main function call
def main(stdscr):
    
    ui_obj = ui.UI()
    status_bar, messages, input_title, input_line, input_box = ui_obj.run_curses(stdscr)
    time_since = int(time.time()) #- (60 * 60 * 24 * search_days)
    relay = args.relay if args.relay else "wss://nos.lol"

    # Load privkey from args, but if not generate a random key for chatting
    privkey = args.privatekey if args.privatekey is not None else secrets.token_bytes(32)

    # Get friendlist - Uses my pubkey as example for now
    my_pubkey = "0497384b57b43c107a778870462901bf68e0e8583b32e2816563543c059784a4"
    friendlist = asyncio.run(get_nip02_friends(relay, my_pubkey, messages))

    # Call the main_task function with the friendlist
    asyncio.run(main_task(relay, status_bar, my_pubkey, privkey, time_since, messages, input_box, client_uuid, friendlist))


# asyncio task gather and handler
async def main_task(relay, status_bar, my_pubkey, privkey, time_since, messages, input_box, client_uuid, friendlist):

    tasks = [
        asyncio.create_task(update_status_bar(relay, status_bar)),
        asyncio.create_task(subscribe_to_notes(relay, status_bar, time_since, messages, client_uuid, friendlist)),
        asyncio.create_task(get_user_input(input_box, privkey, messages, status_bar))
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
