## YAMLIF

YAML InterFace is application that provides user friendly menu hierarchy based on predefined YAML file. User can
traverse the menu hierarchy and edit predefined values. Selected values are saved for further usage.

![yamlif](https://cloud.githubusercontent.com/assets/12072674/11207599/6deb06e8-8d16-11e5-9719-ad7bf67f5222.png)

## License

MIT

This project also includes MIT-licensed `py_curses_editor` written by Scott Hansen. See `LICENSE-editor.md` for license.

## Overview

Interface structure is defined in YAML file. YAML definition file has two basic elements - menu and page. Menu
should contain another menu or submenu. Pages are saved selectively by user into separate file once user presses
S key on the given page. 

Single page can contain any of following elements:

- Checkboxes
- Radio buttons
- Text input (can contain 64 character long value)
- Text area (can contain arbitary value)
- Text display (read only)

Example below defines top menu with title (which should be always present) that contains one page `general_setup` and
one submenu `bus_opts`. Page `general_setup ` contains checkbox `cross_compiler_prefix` that is checked by default and
textbox `kernel_log_buffer` that has default value `64`. Submenu `bus_opts` contains page `pci_access_mode` that
contains a read-only textdisplay element `warning_pci` that is viewable by user. Below the textdisplay there's group
of radiobuttons and one of them is enabled.

YAML file can have predefined shell command that can be executed with R key from menu. Name of command or script
is defined in top menu with `commands` key. This is mostly useful when user wants to do certain external action after
he saves some data.

All objects (`page`, `menu`, `checkbox`) should use unique IDs. Application uses IDs to navigate through the YAML
structure. IDs are not visible in interface, only titles are.

Application also supports validation of user input by custom scripts. Scripts can be defined in python file that
uses same name as YAML file (eg. `page.py` if config file is `page.YAML`). Functions defined in `page.py` can
be called when saving page (eg., `general_setup` calls `general_setup_validator`). These functions should accept
dictionary as input parameter and optionally can return string which will be viewed in UI. See example `page.py`.

## page.yaml example

``` YAML
---
menu: main_menu
title: Example configuration menu
commands: echo "This can contain arbitary shell command or script (eg., ./script.sh)"
content:

  - page: general_setup
    title: General setup
    on_save: general_setup_validator
    content:

      - checkbox: cross_compiler_prefix
        title: Cross-compiler tool prefix
        value: True
        
      - textbox: kernel_log_buffer
        title: Kernel log buffer size
        value: 64


  - menu: bus_opts
    title: BUS options (PCI. etc.)
    content:

      - page: pci_access_mode
        title: PCI access mode
        content:

          - textdisplay: warning_pci
            value: Be careful when changing this value. Default is ANY.

          - radio: BIOS
            title: BIOS

          - radio: ANY
            title: ANY
            value: True
```