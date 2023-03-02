# -*- coding: utf-8 -*-

import asyncio
import curses
from nip01send import broadcast_signed_event, NostrEvent
from commands import CommandHandler
from curses import ascii

relay = "wss://nos.lol" # temp for now until this is a global 


async def get_user_input(input_box, privkey, messages, status_bar):
    loop = asyncio.get_running_loop()
    user_input = ""

    # Enable cursor display and echo user input
    curses.curs_set(1)
    curses.echo()

    while True:
        #messages.addstr("IN THE KB LOOP")
        key = await loop.run_in_executor(None, input_box.getch)
        #if key:
        #    messages.addstr("KEY PRESSED")
        if key == 10:
            if user_input:

                # create NostrEvent instance
                event = NostrEvent(privkey, user_input, [])
                
                # slash command parsing 
                if user_input[:1] == "/":
                    # Command parsing
                    messages.addstr(f" * COMMAND: {user_input}\n")
                    command_handler = CommandHandler()
                    command_handler.handle_command(str(user_input), messages)
                else:
                    # debug
                    #messages.addstr(f" * {user_input}\n")

                    # sign the event 
                    signed_event = await event.sign()

                    # send the event
                    response = await broadcast_signed_event(signed_event, relay)

                user_input = ''          # buggy    # 
                input_box.clear()
                input_box.refresh()
                messages.refresh()
                #break
        elif key == curses.ascii.BS or key == curses.KEY_BACKSPACE or key == 127:
            # Check for the backspace character
            if user_input:
                # Remove the last character from the input string
                user_input = user_input[:-1]
                # Move the cursor back one character and delete it from the input box
                input_box.addstr("\b \b")
        elif key == curses.KEY_RESIZE:
            continue
        elif key >= 32 and key <= 126:
            user_input += chr(key)
        if not key:
            input_box.refresh()
        await asyncio.sleep(0)

    # Disable cursor display and hide user input
    curses.curs_set(0)
    curses.noecho()