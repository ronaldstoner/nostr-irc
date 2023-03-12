# -*- coding: utf-8 -*-

import asyncio
import curses
import json
import re
from nip01send import broadcast_signed_event, NostrEvent
from commands import CommandHandler
from curses import ascii


async def get_user_input(input_box, relay, privkey, messages, status_bar):
    loop = asyncio.get_running_loop()
    user_input = ""
    # Enable cursor display and echo user input
    curses.curs_set(1)
    # Don't echo user input as we will write this ourselves
    curses.noecho()
    input_box.keypad(1)

    while True:
        key = await loop.run_in_executor(None, input_box.getch)

        # User pressed Enter
        if key == 10:
            if user_input:
                # Check if user_input matches regex for nsec key - we do not want users posting these
                if re.search(r'nsec[a-z0-9]{16,}', user_input):
                    messages.addstr("\n *** Error: Potential exposure of nsec private key. Message denied.\n\n", curses.color_pair(1) | curses.A_DIM)
                else:
                    # create NostrEvent instance
                    event = NostrEvent(privkey, user_input, [])
                    
                    # slash command parsing 
                    if user_input[:1] == "/":
                        # Command parsing
                        command_handler = CommandHandler()
                        command_handler.handle_command(str(user_input), messages)
                    else:
                        # Debug
                        #messages.addstr(f" * {user_input}\n")

                        # sign the event 
                        signed_event = await event.sign()

                        # send the event
                        response = await broadcast_signed_event(signed_event, relay)
                        response_json = json.loads(response[1])
                        message_status = response_json[2]
                        if message_status == False:
                            # PoW needed for message - either PoW relay or you're sending too fast
                            messages.addstr(f"\n *** Error: Message failed to send: {response_json[3]}\n\n", curses.color_pair(1) | curses.A_DIM)

                user_input = ''
                input_box.clear()
                input_box.refresh()
                messages.refresh()

        elif key == curses.ascii.BS or key == curses.KEY_BACKSPACE or key == 127:
            # Check for the backspace character
            
            if user_input:
                # Remove the last character from the input string
                user_input = user_input[:-1]

                # Move the cursor back one character and delete it from the input box
                input_box.addstr("\b \b")

                # Refresh the input_box
                input_box.refresh()
        
        elif key == curses.KEY_RESIZE:
            continue

        # Tab auto-complete 
        elif key == curses.ascii.TAB:
            # Tab key pressed - attempt to auto-complete command
            if user_input.startswith("/"):
                command = user_input.split()[0]
                matches = [c for c in CommandHandler().commands if c.startswith(command)]
                if len(matches) == 1:
                    # Only one match - auto-complete the command
                    user_input = matches[0]
                    input_box.clear()
                    input_box.addstr(user_input)
                    input_box.refresh()
                elif len(matches) > 1:
                    # Multiple matches - print the options
                    messages.addstr("\n")
                    for c in matches:
                        messages.addstr(c + " ")
                    messages.addstr("\n")
            else:
                # Auto-complete not supported for non-command inputs
                pass
        # Normal message characters 
        elif key >= 32 and key <= 126:
            user_input += chr(key)
            input_box.addch(key)
        if not key:
            input_box.refresh()
        await asyncio.sleep(0)

    # Disable cursor display and hide user input
    curses.curs_set(0)
    curses.noecho()