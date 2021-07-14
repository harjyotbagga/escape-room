from asciimatics.screen import Screen, KeyboardEvent, MouseEvent
from asciimatics.scene import Scene
from asciimatics.effects import Cycle, Stars
from asciimatics.renderers import FigletText
from time import sleep
import sys
from game_utils import display_dialogue, generate_person
import curses
from sweep_games import game1, game2, game3

if sys.platform == 'darwin':
    window_title = 'Terminal'
elif sys.platform == 'win32':
    window_title == 'python3 sweep.py'
# TODO: Include check for linux distros

worlds = []

curses.initscr()
curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

def demo(screen):
    print('\033[?1003h') # enable mouse tracking with the XTERM API

    texts = [
        'Welcome, janitor, to your first and last day at this nuclear power plant!',
        'You\'ll have three tasks today, after which everyone gets to go home.',
        'Understood? Good, now get to work.',
        'Well done. Truly brilliant. Your scrubbing was incredible.',
        'Damn it, those children are back. I really hope they don\'t-',
        'Well, it appears the children have stolen your legs. No good. But hey, you still '\
        'have arms. We\'ll mount you on a robotic frame and you\'ll get to work.',
        'Nicely done. Now, there\'s one more thing-',
        'Oh no, the children. It would sure be a shame if they-',
        'Good news? The status of your legs has not changed. Bad news? Your '\
        'arms have mysteriously disappeared.',
        'But hey, no problem, you still have your BrainInABox™. Get to work.',
        'Well, uh, I guess you\'re done for the day. Kind of strange how you\'re '\
        'getting paid what, $960,781,132 for a one-time janitorial job? Honestly, '\
        'this sounds like a money-laundering sch-',
        '...',
        'Uh, I\'ll be off. Have a good day sir.'
    ]

    sprite_sequence = {
        0: [0.45, generate_person(), 0.1, generate_person()],
        4: [0.2, generate_person(small=True), generate_person(small=True), 0.25,
            generate_person(), 0.1, generate_person()],
        5: [0.1, generate_person(small=True), generate_person(small=True), 0.35,
            generate_person(legs=False), 0.1, generate_person()],
        6: [0.45, generate_person(legs=False), 0.1, generate_person()],
        7: [0.2, generate_person(small=True), generate_person(small=True), 0.25,
            generate_person(legs=False), 0.1, generate_person()],
        8: [0.1, generate_person(small=True), generate_person(small=True), 0.35,
            generate_person(legs=False, arms=False), 0.1, generate_person()],
        9: [0.45, generate_person(legs=False, arms=False), 0.1, generate_person()],
    }

    screen.clear()
    display_dialogue(screen, texts)




    c = 0
    play = True
    while play:
        

        
        sleep(1 / 60)

Screen.wrapper(demo)