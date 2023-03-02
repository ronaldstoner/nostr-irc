import curses
import asyncio
import sys

class CommandHandler:
    def __init__(self):
        self.commands = {
            '/quit': self.handle_quit,
            '/who': self.handle_who,
            '/part': self.handle_part,
            '/slap': self.handle_slap,
        }

    def handle_command(self, command_string, messages):
        parts = command_string.split(' ')
        command = parts[0]
        arg = None
        if len(parts) > 1:
            arg = parts[1]

        if command in self.commands:
            self.commands[command](arg, messages)

    async def stop_tasks(self, tasks):
        # Cancel all tasks
        for task in tasks:
            task.cancel()
        # Wait for tasks to finish
        await asyncio.gather(*tasks, return_exceptions=True)

    # Quit command - not working gracefully atm TODO: fix this
    def handle_quit(self, arg, messages):
        # Get all running tasks
        #tasks = asyncio.all_tasks()

        # Stop all tasks and wait for them to finish
        #asyncio.run(self.stop_tasks(tasks))

        # Clear and reset the console
        #messages.clear()
        #messages.refresh()

        # Exit curses
        #curses.endwin()

        # Print goodbye message
        #print("Thank you for using nostr-irc.")

        # Exit the program
        sys.exit()


    # Who command
    def handle_who(self, arg, messages):
        # Implement quit logic here
        if not arg:
            messages.addstr(f"WHO COMMAND ENTERED FOR ALL\n")
        else:
            messages.addstr(f"WHO COMMAND ENTERED FOR USER: {arg}\n")
        pass

    # Part command for NIP-4x
    def handle_part(self, arg, messages):
        # Implement part logic here
        messages.addstr("PART COMMAND ENTERED\n")
        pass

    # Slap command
    def handle_slap(self, arg, messages):
        # Implement part logic here
        messages.addstr("SLAP COMMAND ENTERED\n")
        pass