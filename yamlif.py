#!/usr/bin/python3

import sys
import curses
import yaml


def initcurses():
    stdscr = curses.initscr()

    maxy, maxx = stdscr.getmaxyx()

    if maxy < 24 or maxx < 80:
        cleancurses()
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


def cleancurses():
    curses.curs_set(1)
    curses.nocbreak()
    curses.endwin()


def open_yaml(yfile):
    with open(yfile, 'r') as stream:
        yamlobj = yaml.load(stream)
        return yamlobj


def print_structure(yamlobj, lvl=0):
    for obj in yamlobj['content']:
        if 'menu' in obj:
            print('|' + lvl * ' ' + '\\' + ' ' + obj["menu"])
            print_structure(obj, lvl + 1)
        elif 'page' in obj:
            print('|' + lvl * ' ' + '-' + ' ' + obj["page"])


def main():
    if len(sys.argv) < 2:
        print("Please provide a file!")
        quit(1)

    yamlobj = open_yaml(sys.argv[1])
    # print_structure(yamlobj, 0)

    stdscr = initcurses()

    cleancurses()


if __name__ == '__main__':
    main()
