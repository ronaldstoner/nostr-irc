import asyncio
import curses
import time

async def update_status_bar(relay, status_bar):
   while True:
        status_bar.clear()
        y, x = status_bar.getmaxyx()
        # SDTVs and CRTs
        #timestamp = time.strftime("%H:%M:%S")
        # Everything else
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        status_bar.addstr(0, 0, f"{relay}")
        status_bar.addstr(0, x-len(timestamp)-2, timestamp)
        status_bar.refresh()
        status_bar.clear()
        await asyncio.sleep(1)


async def update_user_input():
    curses.curs_set(1)
    user_input = ""
    while True:
        key = input_box.getch()
        if key == 10:
            #break
            messages.addstr(str(f"<HAY ITS ME>: {user_input}"))
            break
        elif key == curses.KEY_BACKSPACE or key == 127:
            user_input = user_input[:-1]
        elif key == curses.KEY_RESIZE:
            continue
        elif key >= 32 and key <= 126:
            user_input += chr(key)
        input_box.addstr(0, 2, user_input)
        input_box.clrtoeol()
        input_box.refresh()
    curses.curs_set(0)
    #messages.addstr(str(user_input))
    await asyncio.sleep(0.01)
