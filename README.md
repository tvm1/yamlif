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
menu: Welcome to main menu!
id: main_menu
content:

  - menu: This is first menu!
    id: first_menu
    content:

      - menu: And this is first submenu.
        id: first_submenu
        
        content:
          - page: This is first page.
            id: first_page
            persistence: True
            type: checkbox
            content:
              - label: First option
                id: foo
                status: False
              - label: Second option
                id: bar
                status: True

  - menu: This will be second menu.
    content:
    
      - page: Second page here.
        id: second_page
        persistence: False
        type: radiobutton
        content:
          - item: First button
            id: foobar
            status: True
          - item: Second button
            id: foobar2
          - item: Third button
            id: foobar3

  - page: Third page.
    id: third_page
    persistence: True
    type: textinput
    content:
      - item: Some arbitary value
        id: foobaz

  - menu: Third menu.
    content:
    
      - page: Fourth page here.
        id: fourth_page
        persistence: True
        type: textarea
        content:
          - item: This is first field
            id: first_field
            length: 20
          - item: Second field
            id: second_field
            length: 15

  - page: The last, fifth page.
    id: fifth_page
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

