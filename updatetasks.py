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
        status_bar.addstr(0, (x - len("Global Feed")) // 2, "Global Feed")
        status_bar.addstr(0, x-len(timestamp)-2, timestamp)
        status_bar.refresh()
        status_bar.clear()
        await asyncio.sleep(1)