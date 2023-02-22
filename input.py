import asyncio
import curses


async def get_user_input(input_box, messages, status_bar):
    loop = asyncio.get_running_loop()
    user_input = ""
    # Move the cursor to the end of the input title
    input_box.move(0, len("<you>: "))

    # Enable cursor display and echo user input
    curses.curs_set(1)
    curses.echo()

    # Read user input one character at a time
    # while True:
    #     char = input_box.getch()
    #     if char == ord('\n'): # If user presses Enter
    #         # Add input to messages and reset input box
    #         messages.addstr(str(f"<you>: {user_input}\n"))
    #         input_box.clear()
    #         input_box.refresh()
    #         # Reset user_input
    #         user_input = ""
    #         #return user_input
    #     elif char == curses.KEY_BACKSPACE or char == curses.KEY_DC: # If user presses Backspace
    #         if user_input: # If there is input to delete
    #             user_input = user_input[:-1] # Remove the last character
    #             #input_box.delch(0, input_box.getyx()[1]-1) # Delete the character from the input box
    #     elif char >= 32 and char <= 126: # If user types a printable character
    #         user_input += chr(char) # Add the character to the input
    #         #input_box.addstr(chr(char)) # Display the character in the input box

    #     input_box.refresh()

    #     # Yield control to the event loop to allow other tasks to run
    #     await asyncio.sleep(0.1)


    # TODO: This blocks other asyncio tasks like subscribe_to_message and updating the status bar. 
    # It does work, but requires the user to press Enter to break out of the while true loop 
    while True:
        #messages.addstr("IN THE KB LOOP")
        key = await loop.run_in_executor(None, input_box.getch)
        #if key:
        #    messages.addstr("KEY PRESSED")
        if key == 10:
            #break
            messages.addstr(str(f"<local_echo_test>: {user_input}\n"))
            input_box.clear()
            input_box.refresh()
            #break
        elif key == curses.KEY_BACKSPACE or key == 127:
            user_input = user_input[:-1]
        elif key == curses.KEY_RESIZE:
            continue
        elif key >= 32 and key <= 126:
            user_input += chr(key)
        if not key:
            input_box.refresh()
        #messages.addstr("AWAITING 0.01")
        await asyncio.sleep(0.01)
        running=True
    #messages.addstr("OUT OF LOOP")
    running=False

    # Disable cursor display and hide user input
    curses.curs_set(0)
    curses.noecho()