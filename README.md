## YAMLIF

YAML InterFace is application that provides user friendly menu hierarchy based on predefined YAML file. User can
traverse the menu hierarchy and edit predefined values. Selected values are saved for further usage.

## License

MIT

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

## TODO

- Page scrolling
- Source file validation

## Some YAML examples

# Basic menu structure

Example below defines top menu with title (which should be always present) that contains one page `general_setup` and
one submenu `bus_opts`. Page general_setup  contains checkbox `cross_compiler_prefix` that is checked by default and
textbox `kernel_log_buffer` that has default value `64`. Submenu `bus_opts` contains page `pci_access_mode` that
contains a read-only textdisplay element `warning_pci` that is viewable by user. Below the textdisplay there's group
of radiobuttons and one of them is enabled.

``` YAML
---
menu: main_menu
title: Example configuration menu
commands: dmesg; read bar
content:

  - page: general_setup
    title: General setup
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