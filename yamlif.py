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


def draw_selector(screen, yamlobj):
    maxy, maxx = screen.getmaxyx()

    cur_id = []

    menu_ids, menu_titles, mid, mtitle = get_menulist(yamlobj, True)
    msel = 0

    cur_id.append(mid)

    size_y = len(menu_titles) + 2
    size_x = len(max(menu_titles, key=len)) + 2

    if size_x < len(mtitle) + 2:
        size_x = len(mtitle) + 2

    pos_y = int(maxy / 2 - size_y / 2)
    pos_x = int(maxx / 2 - size_x / 2)

    screen.addstr(0, 2, ' ARROWS: Move up/down | ENTER/SPACE: Enter menu | ESC: Exit menu | Q: Quit ')
    screen.addstr(maxy - 1, 2, ' Current position: ' + str(''.join(str(e) for e in cur_id)) + ' ')

    win = curses.newwin(size_y, size_x, pos_y, pos_x)

    win.border()
    win.attron(curses.A_BOLD)

    win.addstr(0, int(size_x / 2 - len(mtitle) / 2), mtitle)

    while True:
        for i, mitem in enumerate(menu_titles):
            mitem = mitem.ljust(size_x - 2)
            if msel == i:
                win.addstr(i + 1, 1, str(mitem), curses.color_pair(1))
            else:
                win.addstr(i + 1, 1, str(mitem))

        win.refresh()
        ckey = screen.getch()

        if ckey == curses.KEY_UP:
            if msel == 0:
                msel = len(menu_titles) - 1
            else:
                msel += -1

        if ckey == curses.KEY_DOWN:
            if msel == len(menu_titles) - 1:
                msel = 0
            else:
                msel += 1

        if ckey == curses.KEY_ENTER or ckey == 10 or ckey == ord(" "):
            eltype = get_nodetype(yamlobj, menu_ids[msel])
            if eltype == 'page':
                draw_popup(screen, str("Page view not implemented yet (page id:" + menu_ids[msel] + ")"))
            elif eltype == 'menu':
                # TODO:
                # get_menulist(get_nodecontent(yamlobj, menu_ids[msel]))
                # print(get_nodecontent(yamlobj, menu_ids[msel]))
                pass

            win.border()
            win.refresh()
            screen.addstr(0, 2, ' ARROWS: Move up/down | ENTER/SPACE: Enter menu | ESC: Exit menu | Q: Quit ')
            screen.addstr(maxy - 1, 2, ' Current position: ' + str(''.join(str(e) for e in cur_id)) + ' ')
            win.attron(curses.A_BOLD)
            win.addstr(0, int(size_x / 2 - len(mtitle) / 2), mtitle)

        if ckey == ord("q") or ckey == ord("Q"):
            clean_curses()
            quit(0)


def draw_popup(screen, text='empty'):
    maxy, maxx = screen.getmaxyx()

    size_x = len(text) + 2

    pos_y = int(maxy / 2 - 3)
    pos_x = int(maxx / 2 - size_x / 2)

    win = curses.newwin(3, size_x, pos_y, pos_x)

    win.border()
    win.attron(curses.A_BOLD)

    win.addstr(1, 1, str(text))

    win.getch()
    win.attroff(curses.A_BOLD)

    del win
    screen.touchwin()
    screen.refresh()


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


def get_menulist(yamlobj, root=False):
    menu_ids = []
    menu_titles = []

    if root is True:
        mid = yamlobj['menu']
        mtitle = yamlobj['title']

        for obj in yamlobj['content']:
            if 'menu' in obj:
                menu_ids.append(obj["menu"])
                menu_titles.append(obj["title"])
            elif 'page' in obj:
                menu_ids.append(obj["page"])
                menu_titles.append(obj["title"])
    else:
        mid = yamlobj['menu']
        mtitle = yamlobj['title']
        for obj in yamlobj:
            if 'menu' in obj:
                menu_ids.append(obj["menu"])
                menu_titles.append(obj["title"])
            elif 'page' in obj:
                menu_ids.append(obj["page"])
                menu_titles.append(obj["title"])

    return menu_ids, menu_titles, mid, mtitle


def get_nodetype(obj, objid):
    result = None

    if isinstance(obj, dict):
        for key, val in obj.items():
            if val == objid:
                result = key
            elif isinstance(val, list) or isinstance(val, dict):
                retval = get_nodetype(val, objid)
                if retval is not None:
                    result = retval
    elif isinstance(obj, list):
        for elem in obj:
            if isinstance(elem, list) or isinstance(elem, dict):
                retval = get_nodetype(elem, objid)
                if retval is not None:
                    result = retval
    return result


def get_nodecontent(obj, objid):
    result = None

    if isinstance(obj, dict):
        for key, val in obj.items():
            if val == objid:
                result = obj['content']
            elif isinstance(val, list) or isinstance(val, dict):
                retval = get_nodecontent(val, objid)
                if retval is not None:
                    result = retval
    elif isinstance(obj, list):
        for elem in obj:
            if isinstance(elem, list) or isinstance(elem, dict):
                retval = get_nodecontent(elem, objid)
                if retval is not None:
                    result = retval
    return result


def main():
    if len(sys.argv) < 2:
        print("Please provide a file!")
        quit(1)

    yamlobj = open_yaml(sys.argv[1])
    stdscr = init_curses()

    while True:
        draw_selector(stdscr, yamlobj)

    clean_curses()


if __name__ == '__main__':
    main()
