#!/usr/bin/env python3

import sys
import os
import curses
import curses.textpad
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

    :return: None.
    """
    curses.curs_set(1)
    curses.nocbreak()
    curses.endwin()


def draw_menu(screen, menu_titles, mtitle, msel):
    """
    This function draws a menu with given title and handles the keyboard input.

    :param screen: Screen object.
    :param menu_titles: List of menu titles.
    :param mtitle: Title of currently active menu.
    :param msel: Starting position of cursor in menu.
    :return: Index of selected item.
    """
    maxy, maxx = screen.getmaxyx()

    screen.clear()
    screen.border()
    screen.refresh()

    # calculate minimal menu size to fit content and title
    size_y = len(menu_titles) + 2
    size_x = max(len(max(menu_titles, key=len)), len(mtitle)) + 2

    # calculate position, so the menu is centered
    pos_y = int(maxy / 2 - size_y / 2 - 1)
    pos_x = int(maxx / 2 - size_x / 2)

    screen.addstr(0, 2, ' ARROWS: Move up/down | ENTER/SPACE: Enter menu | ESC: Exit menu | Q: Quit ')

    # create actual window and border
    win = curses.newwin(size_y, size_x, pos_y, pos_x)
    win.border()
    win.attron(curses.A_BOLD)

    # draw title
    win.addstr(0, int(size_x / 2 - len(mtitle) / 2), mtitle)

    # main loop that handles keyboard input and redrawing
    while True:

        # print menu items
        for i, mitem in enumerate(menu_titles):
            mitem = mitem.ljust(size_x - 2)
            if msel == i:
                win.addstr(i + 1, 1, str(mitem), curses.color_pair(1))
            else:
                win.addstr(i + 1, 1, str(mitem))

        win.refresh()
        ckey = screen.getch()

        # read keys and redraw, return item index on ENTER, return -1 if leaving
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


def draw_page(screen, obj, ptitle, msel):
    """
    This functions draws page and its content.

    :param screen: Curses screen object.
    :param obj: Python object ( nested list / dicts ).
    :param ptitle: Page title.
    :param msel: Currently Highlighted item.
    :return: Position of currently selected page element.
    """

    screen.touchwin()
    screen.refresh()

    maxy, maxx = screen.getmaxyx()

    # something to begin with, fit at least page title
    size_y = 2
    size_x = len(ptitle) + 2
    newelem = None

    # determine page height and width
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

                # if it's too long, we will truncate it to five line
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

        # current element requires more space, allocate it
        if width > size_x:
            size_x = width

    # calculate position, so the page is centered
    pos_y = int(maxy / 2 - size_y / 2)
    pos_x = int(maxx / 2 - size_x / 2)

    # create actual window and border
    win = curses.newwin(size_y, size_x, pos_y, pos_x)
    win.border()
    win.attron(curses.A_BOLD)

    # draw title
    win.addstr(0, int(size_x / 2 - len(ptitle) / 2), ptitle)

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
            win.addstr(i + offset, 1, elem.get('title') + ": " + str(elem.get('value', '')), cl)

        elif 'textarea' in elem:
            newelem = 'textarea'
            # check if there's value at all, otherwise leave space blank
            if 'value' not in elem:
                win.addstr(i + offset, 1, str(elem.get('title')) + ": ", cl)
                offset += 1
                break
            else:
                textlist = textwrap.wrap(elem.get('value'), size_x - 4 - len(elem.get('title')))

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

                # print current line
                win.addstr(i + offset, 1, str(ln), cl)
                offset += 1

        # element has changed, add blank line
        if elem != obj[-1]:
            if newelem not in obj[i + 1]:
                offset += 1

    win.attroff(curses.A_BOLD)
    win.refresh()

    ckey = screen.getch()

    # read keys and update, edit value on ENTER, return -1 if leaving
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
        set_value(obj, msel, screen)
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
    :param text: Text to be displayed.
    :return: None.
    """
    maxy, maxx = screen.getmaxyx()

    wrapped = []

    # determine window size
    if len(text) > maxx - 2:

        # popup needs more than one line
        size_x = int(maxx / 1.5) + 2
        wrapped = textwrap.wrap(text, int(maxx / 1.5) - 2)

        if len(wrapped) + 2 > int(maxy / 1.5):
            size_y = int(maxy / 1.5)
    else:
        # popup fits on one line
        size_x = len(text) + 2
        size_y = 3

    # calculate position, so the popup is centered
    pos_y = int(maxy / 2 - size_y / 2)
    pos_x = int(maxx / 2 - size_x / 2)

    # create actual window
    win = curses.newwin(size_y, size_x, pos_y, pos_x)

    start_pos = 0

    while True:

        # clear and redraw
        win.clear()
        win.attron(curses.A_BOLD)
        win.border()
        win.attroff(curses.A_BOLD)

        if len(wrapped) > 0:
            j = 0
            for i in range(1, size_y - 1):
                win.addstr(i, 1, str(wrapped[start_pos + j]))
                j += 1
        else:
            win.addstr(1, 1, str(text))

        win.refresh()
        ckey = screen.getch()

        # read keys scroll and redraw, leave on ENTER / ESC
        if ckey == curses.KEY_UP:
            if start_pos > 0:
                start_pos -= 1
        if ckey == curses.KEY_DOWN:
            if start_pos + size_y - 2 < len(wrapped):
                start_pos += 1
        if ckey == curses.KEY_ENTER or ckey == 10 or ckey == ord(" "):
            break
        if ckey == ord("q") or ckey == ord("Q"):
            clean_curses()
            quit(0)
        if ckey == 27 or ckey == curses.KEY_BACKSPACE:
            break

    del win
    screen.touchwin()
    screen.refresh()


def draw_inputbox(screen, text='empty'):
    """
    Generic function that draws a inputbox in UI.

    :param screen: Curses screen object.
    :param text: Text to be displayed
    :return: value
    """
    maxy, maxx = screen.getmaxyx()

    pos_y = int(maxy / 2 - 1)
    pos_x = int(maxx / 2 - 12)

    win = curses.newwin(3, 25, pos_y, pos_x)
    win.border()
    win.refresh()
    swin = win.derwin(1, 23, 1, 1)

    curses.cbreak()
    curses.curs_set(1)
    screen.keypad(1)

    tpad = curses.textpad.Textbox(swin)
    swin.addstr(0, 0, str(text))
    value = tpad.edit()

    curses.curs_set(0)

    del swin
    del win
    screen.touchwin()
    screen.refresh()

    return value.rstrip()


def draw_inputarea(screen, text='empty'):
    """
    Generic function that draws a 'editor' in UI.

    :param screen: Curses screen object.
    :param text: Text to be displayed
    :return: value
    """
    maxy, maxx = screen.getmaxyx()

    pos_y = int(4)
    pos_x = int(4)

    win = curses.newwin(maxy - 8, maxx - 8, pos_y, pos_x)
    win.border()
    win.refresh()

    swin = win.derwin(maxy - 10, maxx - 10, 1, 1)

    curses.cbreak()
    curses.curs_set(1)
    screen.keypad(1)

    win.addstr(0, 1, 'EMACS-like keys available, CTRL-G to exit')
    win.refresh()

    tpad = curses.textpad.Textbox(swin)
    swin.addstr(0, 0, str(text))
    value = tpad.edit()

    curses.curs_set(0)

    del swin
    del win
    screen.touchwin()
    screen.refresh()

    return value.rstrip()


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

    :param obj: Structure containing YAML object ( nested lists / dictionaries )
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

    :param obj: Structure containing YAML object ( nested lists / dictionaries )
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

    :param obj: Structure containing YAML object ( nested lists / dictionaries ):
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


def set_value(obj, msel, screen):
    """
    Changes value of given YAML object.

    :param obj: Structure containing Python dictionary
    :param msel: Object index to modify
    :param screen: Screen object
    :return: None
    """

    if 'checkbox' in obj[msel]:
        if obj[msel]['value'] is False:
            obj[msel]['value'] = True
        else:
            obj[msel]['value'] = False

    elif 'radio' in obj[msel]:
        obj[msel]['value'] = True

        i = msel + 1

        while i < len(obj):
            if 'radio' in obj[i]:
                obj[i]['value'] = False
                i += 1
            else:
                break

        i = msel - 1

        while i >= 0:
            if 'radio' in obj[i]:
                obj[i]['value'] = False
                i -= 1
            else:
                break

    elif 'textbox' in obj[msel]:

        if 'value' in obj[msel]:
            newval = draw_inputbox(screen, obj[msel]['value'])
            obj[msel]['value'] = str(newval)
        else:
            newval = draw_inputbox(screen, '')
            obj[msel]['value'] = str(newval)

    elif 'textarea' in obj[msel]:

        if 'value' in obj[msel]:
            newval = draw_inputarea(screen, obj[msel]['value'])
            obj[msel]['content'] = str(newval)
        else:
            newval = draw_inputarea(screen, '')
            obj[msel]['content'] = str(newval)

    elif 'textdisplay' in obj[msel]:
        draw_popup(screen, obj[msel]['content'])


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

        msel = draw_menu(stdscr, menu_titles, mtitle, msel)

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
                psel = draw_page(stdscr, get_objectcontent(yamlobj, mid), get_title(yamlobj, mid), psel)
        elif eltype == 'menu':
            mtitle = get_title(yamlobj, mid)
            menu_ids, menu_titles = get_menulist(get_objectcontent(yamlobj, mid))
            msel = 0

    # quit
    clean_curses()
    exit(0)


if __name__ == '__main__':
    main()
