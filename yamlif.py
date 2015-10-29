#!/usr/bin/python3

import sys
import curses
import yaml


def init_curses():
    stdscr = curses.initscr()

    maxy, maxx = stdscr.getmaxyx()

    if maxy < 24 or maxx < 80:
        clean_curses()
        print("Sorry, Only 80x24+ consoles are supported!")
        quit(1)

    curses.start_color()

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    curses.mousemask(1)

    stdscr.clear()
    stdscr.border()
    stdscr.refresh()
    stdscr.keypad(1)

    return stdscr


def clean_curses():
    curses.curs_set(1)
    curses.nocbreak()
    curses.endwin()


def draw_selector(screen, title="empty", menu=None, msel=0):
    if not menu:
        menu = ["empty"]
    maxy, maxx = screen.getmaxyx()

    size_y = len(menu) + 2
    size_x = len(max(menu, key=len)) + 2

    pos_y = int(maxy / 2 - size_y / 2)
    pos_x = int(maxx / 2 - size_x / 2)

    screen.addstr(0, 2, 'Welcome to YAMLIF!')

    win = curses.newwin(size_y, size_x, pos_y, pos_x)

    win.border()
    win.attron(curses.A_BOLD)

    win.addstr(0, int(size_x / 2 - len(title) / 2), title)

    while True:
        for i, mitem in enumerate(menu):
            mitem = mitem.ljust(size_x - 2)
            if msel == i:
                win.addstr(i + 1, 1, str(mitem), curses.color_pair(1))
            else:
                win.addstr(i + 1, 1, str(mitem))

        win.refresh()
        ckey = screen.getch()

        if ckey == curses.KEY_UP:
            if msel == 0:
                msel = len(menu) - 1
            else:
                msel += -1

        if ckey == curses.KEY_DOWN:
            if msel == len(menu) - 1:
                msel = 0
            else:
                msel += 1

        if ckey == curses.KEY_ENTER or ckey == 10:
            del win
            return msel


def open_yaml(yfile):
    with open(yfile, 'r') as stream:
        yamlobj = yaml.load(stream)
        return yamlobj


def print_structure(yamlobj, lvl=0, ):
    for obj in yamlobj['content']:
        if 'menu' in obj:
            print('|' + lvl * ' ' + '\\' + ' ' + obj["menu"])
            if lvl != -1:
                print_structure(obj, lvl + 1)
        elif 'page' in obj:
            print('|' + lvl * ' ' + '-' + ' ' + obj["page"])


def get_menulist(yamlobj):
    menuarr = []

    for obj in yamlobj['content']:
        if 'menu' in obj:
            menuarr.append(obj["menu"])
        elif 'page' in obj:
            menuarr.append(obj["page"])

    return menuarr


def main():
    if len(sys.argv) < 2:
        print("Please provide a file!")
        quit(1)

    yamlobj = open_yaml(sys.argv[1])
    stdscr = init_curses()

    draw_selector(stdscr, title="Main menu", menu=get_menulist(yamlobj))

    clean_curses()


if __name__ == '__main__':
    main()
