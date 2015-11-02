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
            content:
              - checkbox: my_setting_1
                title: Test setting 1
                status: False
              - checkbox: my_setting_2
                title: Test setting 2
                status: True
              - radio: radio_211
                title: Test radiobutton 211
                status: False
              - radio: radio_222
                title: Test radiobutton 222
                status: True
              - radio: radio_333
                title: Test radiobutton 333
                status: False
              - textbox: value_500
                title: Text value 500
              - textbox: value_501
                title: Text value 501
              - textbox: value_502
                title: Text value 502
              - textarea: text_area_101
                title: Text area 101
                length: 20
              - textarea: text_area_102
                title: Text area 102
                length: 15
              - textdisplay: warning_1
                content: >
                  Warning:
                  This is just experiment.
                  Be careful.
                  Thanks!

      - menu: second_submenu
        title: And this is second submenu.
        content:
          - page: sixth_page
            title: This is sixth page.
            persistence: False
            content:
              - radio: radio_11
                title: Test radiobutton 1
                status: False
              - radio: radio_22
                title: Test radiobutton 2
                status: True

  - menu: second_menu
    title: This will be second menu.
    content:
      - page: second_page
        title: Second page here.
        persistence: False
        content:
          - textbox: value_1
            title: Text value 1
          - textbox: value_2
            title: Text value 2
          - textbox: value_3
            title: Text value 3

  - page: third_page
    title: Third page.
    persistence: True
    content:
      - checkbox: some_other_value_1
        title: Check me!
        status: False

  - menu: third_menu
    title: Third menu.
    content:
      - page: fourth_page
        title: Fourth page here.
        persistence: True
        content:
          - textarea: text_area_10
            title: First text area
            length: 20
          - textarea: text_area_20
            title: Second text area
            length: 15

  - page: fifth_page
    title: The last, fifth page.
    persistence: False
    content:
      - textdisplay: warning_1
        content: >
          This
          is
          very
          long
          text.
```