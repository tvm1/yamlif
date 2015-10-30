## YAMLIF

YAML InterFace is application that provides user friendly menu hierarchy based on predefined YAML file. User can
traverse the menu hierarchy and edit predefined values. Selected values are saved for further usage. 

## Overview

Menu hierarchy is specified in YAML file. Basic element is page. Multiple pages can be contained in common menu.
Every page can be selectively saved by the user. Page can have optional on_save binding that is called on the selected
dataset. Such binding can modify values in the dataset and output text or result back to the user interface. Whole menu
hierarchy has one final DONE function that can execute predefined external commands with access to values that were
set by the user.

Single page can contain one of following elements:

- Checkboxes
- Radio buttons
- Text input
- Text area
- Text display (read only)

## Menu definition file

See example below.

``` yaml
---
menu: main_menu
title: Welcome to main menu!
content:

  - menu: first_menu
    title: This is first menu!
    content:

      - menu: first_submenu
        title: And this is first submenu.
        content:
          - page: first_page
            title: This is first page.
            persistence: True
            type: checkbox
            content:
              - label: First option
                title: foo
                status: False
              - label: Second option
                title: bar
                status: True

      - menu: second_submenu
        title: And this is second submenu.
        content:
          - page: sixth_page
            title: This is sixth page.
            persistence: False
            type: checkbox
            content:
              - label: First option
                title: foobaz
                status: False
              - label: Second option
                title: foobar
                status: True

  - menu: second_menu
    title: This will be second menu.
    content:
      - page: second_page
        title: Second page here.
        persistence: False
        type: radiobutton
        content:
          - item: First button
            title: foobar
            status: True
          - item: Second button
            title: foobar2
          - item: Third button
            title: foobar3

  - page: third_page
    title: Third page.
    persistence: True
    type: textinput
    content:
      - item: Some arbitary value
        title: foobaz

  - menu: third_menu
    title: Third menu.
    content:
      - page: Fourth page here.
        title: fourth_page
        persistence: True
        type: textarea
        content:
          - item: This is first field
            title: first_field
            length: 20
          - item: Second field
            title: second_field
            length: 15

  - page: fifth_page
    title: The last, fifth page.
    persistence: False
    type: textdisplay
    content:
      - item: Warning.
        content: >
          This
          is
          very
          long
          text.
```