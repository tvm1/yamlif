#!/usr/bin/env python3

import sys
import os
import curses
import textwrap
import re

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

    pos_y = int(maxy / 2 - size_y / 2 - 1)
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

        if ckey == 27 or ckey == curses.KEY_BACKSPACE:
            return -1

    win.refresh()

    del win
    screen.touchwin()
    screen.refresh()


def draw_page(screen, yamlobj, obj, mtitle, msel):
    """
    This functions draws page and it's content.

    :param screen: Curses screen object.
    :param yamlobj: Whole python object ( nested list / dicts )
    :param obj: Python object ( nested list / dicts )
    :param mid: Page id
    :param mtitle: Page title
    :return: Position of currently selected page element
    """

    screen.touchwin()
    screen.refresh()

    maxy, maxx = screen.getmaxyx()

    size_y = 2
    size_x = len(mtitle) + 2
    newelem = None

    # calculate page height and width
    for i, elem in enumerate(obj):

        if elem.get('value') is None:
            value_length = 0
        else:
            value_length = len(str(elem.get('value')))

        if 'checkbox' in elem:
            size_y += 1
            width = len(elem.get('title')) + 6
            newelem = 'checkbox'
        elif 'radio' in elem:
            size_y += 1
            width = len(elem.get('title')) + 6
            newelem = 'radio'
        elif 'textbox' in elem:
            size_y += 1
            width = len(elem.get('title')) + value_length + 4
            newelem = 'textbox'
        elif 'textarea' in elem:
            size_y += 5
            width = int(maxx / 2)
            newelem = 'textarea'
        elif 'textdisplay' in elem:

            # wrapping is handled here
            if len(elem.get('content')) > int(maxx / 2):
                width = int(maxx / 2)
                wrapped = textwrap.wrap(elem.get('content'), int(maxx / 2) - 2)

                # if it's too long, we will truncate it
                if len(wrapped) > 4:
                    size_y += 5
                else:
                    size_y += len(wrapped)
            else:
                # it's only one line
                width = len(elem.get('content')) + 2
                size_y += 1

            newelem = 'textdisplay'

        # element has changed, add blank line
        if elem != obj[-1]:
            if newelem not in obj[i + 1]:
                size_y += 1

        if width > size_x:
            size_x = width

    pos_y = int(maxy / 2 - int(size_y / 2))
    pos_x = int(maxx / 2 - size_x / 2)

    win = curses.newwin(size_y, size_x, pos_y, pos_x)

    win.border()
    win.attron(curses.A_BOLD)

    win.addstr(0, int(size_x / 2 - len(mtitle) / 2), mtitle)

    newelem = None
    offset = 1

    # main loop that draws page
    for i, elem in enumerate(obj):

        # color for currently selected item
        if i == msel:
            cl = curses.color_pair(1)
        else:
            cl = curses.color_pair(0)

        # this actually draws what is visible
        if 'checkbox' in elem:
            newelem = 'checkbox'
            if elem['value'] is True:
                win.addstr(i + offset, 1, '[*] ' + elem.get('title'), cl)
            else:
                win.addstr(i + offset, 1, '[ ] ' + elem.get('title'), cl)
        elif 'radio' in elem:
            newelem = 'radio'
            if elem['value'] is True:
                win.addstr(i + offset, 1, '(*) ' + elem.get('title'), cl)
            else:
                win.addstr(i + offset, 1, '( ) ' + elem.get('title'), cl)
        elif 'textbox' in elem:
            newelem = 'textbox'

            if elem.get('value') is None:
                value = ''
            else:
                value = str(elem.get('value'))

            win.addstr(i + offset, 1, elem.get('title') + ": " + value, cl)
        elif 'textarea' in elem:
            newelem = 'textarea'

            # check if there's value at all, otherwise leave space blank
            if 'content' not in elem:
                win.addstr(i + offset, 1, str(elem.get('title')) + ": ", cl)
                offset += 5
                break
            else:
                textlist = textwrap.wrap(elem.get('content'), size_x - 2 - len(elem.get('title')))

            # print content of the textarea
            for j, ln in enumerate(textlist):

                # if it's too many lines, truncate
                if j == 4 and len(textlist) > 4:
                    ln = re.sub('.............$', '... [wrapped]', ln)
                    win.addstr(i + offset, 1 + len(elem.get('title')) + 2, str(ln), cl)
                    break

                if j == 0:
                    win.addstr(i + offset, 1, str(elem.get('title')) + ": " + str(ln), cl)
                    offset += 1
                else:
                    win.addstr(i + offset, 1 + len(elem.get('title')) + 2, str(ln), cl)
                    offset += 1

        elif 'textdisplay' in elem:
            newelem = 'textdisplay'

            # wrapping is handled here
            textlist = textwrap.wrap(elem.get('content'), size_x - 2)

            # print whatever is in content of textdisplay
            for j, ln in enumerate(textlist):

                # if it's too many lines, truncate
                if j == 4 and len(textlist) > 4:
                    ln = re.sub('.............$', '... [wrapped]', ln)
                    win.addstr(i + offset, 1, str(ln), cl)
                    break

                win.addstr(i + offset, 1, str(ln), cl)
                offset += 1

        # element has changed, add blank line
        if elem != obj[-1]:
            if newelem not in obj[i + 1]:
                offset += 1

    win.attroff(curses.A_BOLD)
    win.refresh()

    ckey = screen.getch()

    if ckey == curses.KEY_UP:
        if msel == 0:
            msel = len(obj) - 1
        else:
            msel -= 1

    elif ckey == curses.KEY_DOWN:
        if msel == len(obj) - 1:
            msel = 0
        else:
            msel += 1

    elif ckey == curses.KEY_ENTER or ckey == 10 or ckey == ord(" "):
        set_value(obj[msel])

    elif ckey == ord("q") or ckey == ord("Q"):
        clean_curses()
        quit(0)

    elif ckey == 27 or ckey == curses.KEY_BACKSPACE:
        msel = -1

    del win
    screen.touchwin()
    screen.refresh()

    return msel


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


def set_value(obj):
    """
    Changes value of given YAML object.

    :param obj: Structure containing Python dictionary
    :return: None
    """

    if 'checkbox' in obj:
        if obj['value'] == False:
            obj['value'] = True
        else:
            obj['value'] = False


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
            psel = 0
            while psel != -1:
                psel = draw_page(stdscr, yamlobj, get_objectcontent(yamlobj, mid), get_title(yamlobj, mid), psel)
        elif eltype == 'menu':
            mtitle = get_title(yamlobj, mid)
            menu_ids, menu_titles = get_menulist(get_objectcontent(yamlobj, mid))
            msel = 0

    # quit
    clean_curses()
    exit(0)


if __name__ == '__main__':
    main()
