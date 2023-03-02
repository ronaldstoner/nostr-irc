# -*- coding: utf-8 -*-

import curses

class UI:
    def __init__(self):
        self.status_bar = None
        self.messages = None
        self.input_line = None
        self.input_box = None

    def run_curses(self, stdscr):
        self.status_bar = curses.newwin(1, curses.COLS, 0, 0)
        self.status_bar.bkgd(" ", curses.color_pair(2))
        self.status_bar.scrollok(True)
        self.status_bar.refresh()

        self.messages = curses.newwin(curses.LINES - 3, curses.COLS, 2, 0)
        self.messages.bkgd(" ", curses.color_pair(1))
        self.messages.scrollok(True)
        self.messages.refresh()

        input_title = "<you>: "
        input_title_length = len(input_title)
        self.input_line = curses.newwin(1, curses.COLS, curses.LINES - 1, 0)
        self.input_line.bkgd(" ", curses.color_pair(2))
        self.input_line.addstr(0, 0, input_title, curses.A_BOLD)
        self.input_line.refresh()

        self.input_box = curses.newwin(1, curses.COLS, curses.LINES - 1, input_title_length)
        self.input_box.bkgd(" ", curses.color_pair(2))
        self.input_box.refresh()

        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Regular text
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)     # Inverted status bar text
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Unknown pubkeys
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # System messages
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)                    # Orange - Following

        return self.status_bar, self.messages, input_title, self.input_line, self.input_box

