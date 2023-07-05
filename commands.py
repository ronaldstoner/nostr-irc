import curses
import asyncio
import os
import sys

from nip01 import nip_05_identifiers

class CommandHandler:

    def __init__(self):
        self.commands = {
            '/clear': self.handle_clear,
            '/join': self.handle_join,            
            '/part': self.handle_part,
            '/quit': self.handle_quit,
            '/slap': self.handle_slap,
            '/who': self.handle_who,
        }

    def handle_command(self, command_string, messages):
        parts = command_string.split(' ')
        command = parts[0]
        arg = None
        if len(parts) > 1:
            arg = parts[1]

        if command in self.commands:
            self.commands[command](arg, messages)

    def stop_tasks(self, tasks):
        # Cancel all tasks
        for task in tasks:
            task.cancel()

    # Clear command
    def handle_clear(self, arg, messages):
        messages.clear()
        messages.refresh()
        pass

    # Join command
    def handle_join(self, arg, messages):
        # Implement part logic here
        messages.addstr("\n *** JOIN COMMAND ENTERED\n")
        messages.refresh()
        pass

    # Part command 
    def handle_part(self, arg, messages):
        # Implement part logic here
        messages.addstr("\n *** PART COMMAND ENTERED\n")
        messages.refresh()
        pass

    # Quit command
    def handle_quit(self, arg, messages):
        # Get all running tasks
        tasks = asyncio.all_tasks()

        # Stop all tasks and wait for them to finish
        self.stop_tasks(tasks)

        # Clear and reset the console
        messages.clear()
        messages.refresh()

        # Exit curses
        curses.endwin()

        # Clearing the Screen
        # Linux/Mac
        if(os.name == 'posix'):
           os.system('clear')
        # Windows
        else:
           os.system('cls')

        # Print goodbye message
        print("Thank you for using nostr-cli.")

    # Slap command
    def handle_slap(self, arg, messages):
        # Implement part logic here
        messages.addstr("\n *** SLAP COMMAND ENTERED\n")
        messages.refresh()
        pass

    # Who command
    def handle_who(self, arg, messages):
        if not arg:
            # Top 20 recent users plus user count
            # TODO: Add timestamps and actually make this recent
            top_names = sorted(nip_05_identifiers.items(), key=lambda x: x[1])[:20]
            remaining_names_tally = len(nip_05_identifiers) - len(top_names)
            result_string = ', '.join([f'{name}' for pubkey, name in top_names]) + f' and {remaining_names_tally} other users'
            messages.addstr(f"\n *** Recent Users: {result_string}\n\n", curses.color_pair(1) | curses.A_DIM)
        else:
            messages.addstr(f"\n *** WHO COMMAND ENTERED FOR USER: {arg}\n")
            messages.refresh()
