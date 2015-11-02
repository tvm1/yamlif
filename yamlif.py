#!/usr/bin/env python3

import sys
import os
import curses

try:
    import yaml
except ImportError:
    print("This application requires PYYAML module to work correctly. See: http://pyyaml.org")
    quit(1)


def init_curses():
    """
    This function sets up basic curses environment.

    :return: Screen object.
    """
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
    """
    Cleans up curses after quit.

    :return: None
    """
    curses.curs_set(1)
    curses.nocbreak()
    curses.endwin()


def draw_selector(screen, menu_titles, mtitle, msel):
    """
    This function draws a menu with given title and handles the keyboard input.

    :param screen: Screen object.
    :param menu_titles: List of menu titles.
    :param mtitle: Title of currently active menu
    :param msel: Starting position of cursor in menu.
    :return: Index of selected item.
    """
    maxy, maxx = screen.getmaxyx()

    screen.clear()
    screen.border()
    screen.refresh()

    size_y = len(menu_titles) + 2
    size_x = len(max(menu_titles, key=len)) + 2

    if size_x < len(mtitle) + 2:
        size_x = len(mtitle) + 2

    pos_y = int(maxy / 2 - size_y / 2)
    pos_x = int(maxx / 2 - size_x / 2)

    screen.addstr(0, 2, ' ARROWS: Move up/down | ENTER/SPACE: Enter menu | ESC: Exit menu | Q: Quit ')

    win = curses.newwin(size_y, size_x, pos_y, pos_x)

    win.border()
    win.attron(curses.A_BOLD)

    win.addstr(0, int(size_x / 2 - len(mtitle) / 2), mtitle)

    # main loop that handles keyboard input and redrawing
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
            del win
            return msel

        if ckey == ord("q") or ckey == ord("Q"):
            clean_curses()
            quit(0)

        if ckey == 27:
            return -1

    win.refresh()


def draw_popup(screen, text='empty'):
    """
    Generic function that draws a popup window in UI.

    :param screen: Curses screen object.
    :param text: Text to be displayed
    :return: None
    """
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
    """
    This function opens file with YAML configuration.

    :param yfile: Name of file
    :return: Python object ( nested lists / dicts )
    """
    with open(yfile, 'r') as stream:
        yamlobj = yaml.load(stream)
        return yamlobj


def get_menulist(yamlobj, root=False):
    """
    This function parses objects returned by get_menucontent() and prepares input for
    draw_selector().

    :param yamlobj: Python object ( nested list / dicts )
    :param root: True only if parsing YAML hierarchy from top.
    :return: menu_ids - list of IDs, menu_titles - list of menu titles
    """
    menu_ids = []
    menu_titles = []

    if root is True:

        for obj in yamlobj['content']:
            if 'menu' in obj:
                menu_ids.append(obj["menu"])
                menu_titles.append(obj["title"])
            elif 'page' in obj:
                menu_ids.append(obj["page"])
                menu_titles.append(obj["title"])
    else:
        for obj in yamlobj:
            if 'menu' in obj:
                menu_ids.append(obj["menu"])
                menu_titles.append(obj["title"])
            elif 'page' in obj:
                menu_ids.append(obj["page"])
                menu_titles.append(obj["title"])

    return menu_ids, menu_titles


def get_nodetype(obj, objid):
    """
    Returns key of the object with given ID. (eg., menu, page, etc. )

    :param obj Structure containing YAML object ( nested lists / dictionaries ):
    :param objid: YAML ID of given node
    :return: Key of given ID
    """
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


def get_title(obj, objid):
    """
    Returns title value of the object with given ID.

    :param obj Structure containing YAML object ( nested lists / dictionaries ):
    :param objid: YAML ID of given node
    :return: Title of given ID
    """

    result = None

    if isinstance(obj, dict):
        for key, val in obj.items():
            if val == objid:
                result = obj['title']
            elif isinstance(val, list) or isinstance(val, dict):
                retval = get_title(val, objid)
                if retval is not None:
                    result = retval
    elif isinstance(obj, list):
        for elem in obj:
            if isinstance(elem, list) or isinstance(elem, dict):
                retval = get_title(elem, objid)
                if retval is not None:
                    result = retval
    return result


def get_objectcontent(obj, objid):
    """
    Returns list / dictionary structure that is content of given YAML ID.

    :param obj Structure containing YAML object ( nested lists / dictionaries ):
    :param objid: YAML ID of given node
    :return: Nested list / dictionary
    """
    result = None

    if isinstance(obj, dict):
        for key, val in obj.items():
            if val == objid:
                result = obj['content']
            elif isinstance(val, list) or isinstance(val, dict):
                retval = get_objectcontent(val, objid)
                if retval is not None:
                    result = retval
    elif isinstance(obj, list):
        for elem in obj:
            if isinstance(elem, list) or isinstance(elem, dict):
                retval = get_objectcontent(elem, objid)
                if retval is not None:
                    result = retval
    return result


def main():
    """
    Contains main loop that loads YAML, draws menu and decides what to do with selected items.

    :return: Exit value
    """
    # fix the curses ESCAPE key delay
    os.environ['ESCDELAY'] = '0'

    if len(sys.argv) < 2:
        print("Please provide a file!")
        quit(1)

    # start with first item selected
    msel = 0

    # open file & set up screen
    yamlobj = open_yaml(sys.argv[1])
    stdscr = init_curses()

    # top menu defaults
    mhist = []
    mid = yamlobj['menu']
    mtitle = yamlobj['title']
    mhist.append(mid)

    # get content for the first menu
    menu_ids, menu_titles = get_menulist(yamlobj, True)

    # main loop that draws menu and allows to traverse & open menu items
    while True:

        msel = draw_selector(stdscr, menu_titles, mtitle, msel)

        # leaving menu and going back to top
        if msel == -1:
            if len(mhist) > 1:
                mhist.pop()
                mid = mhist.pop()
            else:
                msel = 0
                continue
        else:
            mid = menu_ids[msel]

        eltype = get_nodetype(yamlobj, mid)

        if eltype == 'menu':
            mhist.append(mid)

        # determine what we try to open and act accordingly
        if eltype == 'page':
            foo = get_objectcontent(yamlobj, mid)
            draw_popup(stdscr, str("Page view not implemented yet (page id:" + mid + ")"))
        elif eltype == 'menu':
            mtitle = get_title(yamlobj, mid)
            menu_ids, menu_titles = get_menulist(get_objectcontent(yamlobj, mid))
            msel = 0

    # quit
    clean_curses()
    exit(0)


if __name__ == '__main__':
    main()
