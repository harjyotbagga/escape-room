from asciimatics.event import KeyboardEvent
from asciimatics.scene import Scene
import pygetwindow as gw
from asciimatics.screen import Screen
from math import floor
from time import sleep
import asyncio
import curses
from asciimatics.exceptions import ResizeScreenError

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

    screen.move(box_x + box_width, box_y + box_height)
    screen.draw(box_x + box_width, box_y, char='|')

    screen.move(box_x, box_y + box_height)
    screen.draw(box_x, box_y, char='|')

    screen.move(box_x, box_y)
    screen.draw(box_x + box_width + 1, box_y, char='-')

    screen.move(box_x, box_y + box_height)
    screen.draw(box_x + box_width + 1, box_y + box_height, char='-')

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
            screen.wait_for_input(cont_msg_blink_time) # wait for the blink amount of time
            await asyncio.sleep(0) # senc control back over to the blink func
            event = screen.get_event()
            if event and isinstance(event, KeyboardEvent):
                awaiting_press = False
                break

    async def do_cont():
        nonlocal awaiting_press
        awaiting_press = True
        await asyncio.gather(blink_cont_text(), await_cont_inp())
        
        screen.print_at(' ' * len(cont_msg), cont_msg_x, cont_msg_y)

        # you know, apparently, i am a huge fucking dumbass. apparently, concurrent != parallel, and
        # asyncio does concurrent

    for line in dialogue:
        # Clear box space for dialogue
        for y in range(box_y + 1, box_y + box_height):
            screen.move(box_x + 1, y)
            screen.draw(box_x + box_width - 1, y, char=' ')

        words = line.split()
        rows = []
        cur_row = []
        len_sum = 0
        for word in words:
            if len_sum + len(word) > line_length:
                rows.append(' '.join(cur_row))
                if len(word) > line_length:
                    for i in range(0, len(word) - len(word) % line_length, line_length):
                        rows.append(word[i:i + line_length + 1])
                    cur_row.append(word[i + line_length + 1:])
                    len_sum = len(word[i + line_length + 1:]) + 1
                else:
                    cur_row = [word]
                    len_sum = len(word) + 1
            else:
                cur_row.append(word)
                len_sum += len(word) + 1

        if cur_row:
            rows.append(' '.join(cur_row))

        key_pressed = False

        for i, l in enumerate(rows):
            for j, c in enumerate(l):
                x = j + box_x + text_margin + 1
                y = i + box_y + 1

                screen.print_at(c, x, y) # draw current line char
                screen.refresh()

                event = screen.get_event()
                if event and isinstance(event, KeyboardEvent): # check if a key was pressed
                    # if it was, leave, and mark it as so
                    key_pressed = True
                    break

                sleep(char_time)
            if key_pressed: # if a key was pressed
                break # leave

        # draw rest in case a key was pressed
        if key_pressed:
            for i, l in enumerate(rows):
                for j, c in enumerate(l):
                    x = j + box_x + text_margin + 1
                    y = i + box_y + 1
                    screen.print_at(c, x, y) # draw current line char
                    screen.refresh()
            # i know that it can be optimized, but cmon, the O notation wont change
        
        asyncio.run(do_cont())

def set_screen_size(screen, target_dimensions, leniency=10):
        tw, th = target_dimensions
        w, h = screen.width, screen.height

        def _set_screen_size(t_screen):
            nonlocal w, h, screen
            screen = t_screen
            w, h = screen.width, screen.height
            
            screen.move(0, 0)
            screen.draw(tw - 1, 0)
            screen.draw(tw - 1, th - 1)
            screen.draw(0, th - 1)
            screen.draw(0, 0)

            wmsg = '                                        '
            if w < tw - leniency:
                wmsg = 'Please increase this window\'s width'
            if w > tw + leniency:
                wmsg = 'Please decrease this window\'s width'

            hmsg = '                                         '
            if h < th - leniency:
                hmsg = 'Please increase this window\'s height'
            if h > th + leniency:
                hmsg = 'Please decrease this window\'s height'

            pw = w if tw > w else tw
            ph = h if th > h else th
            screen.print_at(wmsg, pw // 2 - len(wmsg) // 2, ph // 2)
            screen.print_at(hmsg, pw // 2 - len(hmsg) // 2, ph // 2 + 1)
            screen.refresh()

            while not screen.has_resized():
                pass
        
        while abs(screen.width - tw) > leniency or abs(screen.height - th) > leniency:
            Screen.wrapper(_set_screen_size)
        
        return screen

def restart_mouse_tracking():
    curses.initscr()
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

    print('\033[?1003h') # enable mouse tracking with the XTERM API

def display_help(screen, help):
    helps = help.split('\n')
    mlen = len(max(helps, key=len))
    screen.move(screen.width // 2 - mlen // 2 - 2, screen.height // 2 - len(helps) // 2 - 1)
    screen.draw(screen.width // 2 + mlen // 2 + 2, screen.height // 2 - len(helps) // 2 - 1)
    screen.draw(screen.width // 2 + mlen // 2 + 2, screen.height // 2 + len(helps) // 2 + 2)
    screen.draw(screen.width // 2 - mlen // 2 - 2, screen.height // 2 + len(helps) // 2 + 2)
    screen.draw(screen.width // 2 - mlen // 2 - 2, screen.height // 2 - len(helps) // 2 - 1)
    for i, h in enumerate(helps):
        screen.print_at(h, screen.width // 2 - len(h) // 2, screen.height // 2 - len(helps) // 2 + i + 1)
    screen.refresh()


def update_gun_ui(shooter_face='😃', gun_sprite='︻デ═一', bullets_remaining=3):
    pass