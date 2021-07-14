from asciimatics.event import KeyboardEvent
import pygetwindow as gw
from asciimatics.screen import Screen
from math import floor
from time import sleep
import asyncio

def generate_person(arms=True, legs=True, small=False, hands_raised=False) -> None:
    if not small:
        person = ''' O
/|\\
|
/ \\
'''
        limb_filter = [
            0, 0,
            1, 0, 1,
            0, 0,
            2, 0, 2,
        ]
    else:
        person = ''' O
/|\\
/ \\
'''
        limb_filter = [
                0, 0,
                1, 0, 1,
                2, 0, 2
            ]
    person = list(person)
    ret = 0
    for i in range(len(person)): 
        if person[i] == '\n': ret += 1; continue
        if limb_filter[i - ret] == 1 and not arms:
            person[i] = ' '
        if limb_filter[i - ret] == 1 and hands_raised:
            if person[i] == '/': person[i] = '\\'
            elif person[i] == '\\': person[i] = '/'

        if limb_filter[i - ret] == 2 and not legs:
            person[i] = ' '

    person = ''.join(person)

    return person

def get_window_rect(window_title):
    titles = gw.getAllTitles()
    full_title = next((x for x in titles if bytes(window_title, "utf-8") in bytes(x, 'utf-8')), None)
    
    if full_title is None:
        return None

    window_rects = []
    for w in gw.getWindowsWithTitle(full_title):
        window_rects.append((w.left, w.top, w.width, w.height))
    return window_rects

def display_dialogue(screen: Screen, dialogue, char_time: float = 0.03, text_height: float = 0.6, box_dimensions=(50, 5), text_margin: int = 1):
    box_width, box_height = box_dimensions
    box_x, box_y = screen.width // 2 - box_width // 2, int(screen.height * text_height)

    screen.move(box_x, box_y)

    screen.draw(box_x + box_width, box_y)
    screen.draw(box_x + box_width, box_y + box_height)
    screen.draw(box_x, box_y + box_height)
    screen.draw(box_x, box_y)

    line_length = (box_width - (1 + text_margin) * 2)
    cont_msg = '<Press any key to continue>'
    cont_msg_x = box_x + box_width // 2 - len(cont_msg) // 2
    cont_msg_y = box_y + box_height + 2
    cont_msg_blink_time = 0.8

    awaiting_press = False

    async def blink_cont_text():
        while awaiting_press:
            screen.print_at(cont_msg, cont_msg_x, cont_msg_y)
            screen.refresh()
            await asyncio.sleep(0) # turn on the message and send control back
            screen.print_at(' ' * len(cont_msg), cont_msg_x, cont_msg_y)
            screen.refresh()
            await asyncio.sleep(0) # turn off the message and send control back
        
    async def await_cont_inp():
        nonlocal awaiting_press
        while awaiting_press:
            # this is the worst fucking thing i've ever wrote. TODO: figure out how the fuck asyncio works, cuz the docs sure don't help!
            # i thought gather launched things asynchronously, but nope, i have to do this terribleness to get it to work
            screen.wait_for_input(cont_msg_blink_time) # wait for the blink amount of time
            await asyncio.sleep(0) # senc control back over to the blink func
            event = screen.get_event()
            if event and isinstance(event, KeyboardEvent):
                awaiting_press = False
                break
            # the worst part of this is that it works

    async def do_cont():
        nonlocal awaiting_press
        awaiting_press = True
        await asyncio.gather(blink_cont_text(), await_cont_inp())
        
        screen.print_at(' ' * len(cont_msg), cont_msg_x, cont_msg_y)

    for line in dialogue:
        # Clear box space for dialogue
        for y in range(box_y + 1, box_y + box_height):
            screen.move(box_x + 1, y)
            screen.draw(box_x + box_width - 1, y, char=' ')

        for i, c in enumerate(line):
            x = box_x + 1 + text_margin \
                + i % line_length
            y = box_y + 1 \
                + floor(i / line_length)

            screen.print_at(c, x, y) # draw current line char
            screen.refresh()

            event = screen.get_event()
            if event and isinstance(event, KeyboardEvent): # check if a key was pressed
                # if it was, draw out the rest of the line and leave
                for j in range(i + 1, len(line)):
                    x = box_x + 1 + text_margin \
                        + j % line_length
                    y = box_y + 1 \
                        + floor(j / line_length)
                    screen.print_at(line[j], x, y)

                screen.refresh()
                break

            sleep(char_time)
        
        asyncio.run(do_cont())
        
