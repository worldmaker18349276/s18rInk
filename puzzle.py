import curses

use_unicode = True
pzl_str = """
.3.112.2..
.3..3.1312
22.1......
.3..3..2.2
2.....2.21
31.3.....3
2.2..3..2.
......1.32
2220.3..3.
..3.122.2.
"""


if use_unicode:
    chars = ["０", "１", "２", "３", "４", "　"]
    spins = ["◴ ", "◵ ", "◶ ", "◷ "]
else:
    chars = [" 0", " 1", " 2", " 3", " 4", "  "]
    spins = ["|", "\\", "-", "/"]


try:
    screen = curses.initscr()
    screen.keypad(1)
    curses.curs_set(0)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.mouseinterval(0)
    print("\033[?1002h\n")
    curses.flushinp()
    curses.noecho()
    screen.clear()

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    screen.bkgd(" ", curses.color_pair(1))

    BUTTON_SCROLLUP   = 0x0001_0000
    BUTTON_SCROLLDOWN = 0x0020_0000
    BUTTON_DRAG       = 0x1000_0000
    BUTTON13_PRESSED  = curses.BUTTON1_PRESSED | curses.BUTTON3_PRESSED

    nums = {".":-1, "0":0, "1":1, "2":2, "3":3, "4":4}
    attrs = {False: curses.color_pair(1),
             True : curses.color_pair(1) | curses.A_REVERSE,
             }
    pzl = [[nums[ch] for ch in line] for line in pzl_str.strip().split()]
    chk = [[False for n in line] for line in pzl]
    chk_ = [[c for c in line] for line in chk]

    yran = range(2, len(pzl)+2, 1)
    xran = range(2, len(pzl[0])*2+2, 2)
    for y, line, line2 in zip(yran, pzl, chk):
        for x, n, c in zip(xran, line, line2):
            screen.addstr(y, x, chars[n], attrs[c])

    count = 0
    check1 = True
    check2 = False
    check = check1
    screen.addstr(0, 0, "F", attrs[check1])
    screen.addstr(0, 1, "B", attrs[check2])

    while True:
        key = screen.getch()
        if key == 27:
            break

        elif key == ord("x"):
            chk_ = [[c for c in line] for line in chk]

        elif key == ord("z"):
            chk = [[c for c in line] for line in chk_]

            for y, line, line2 in zip(yran, pzl, chk):
                for x, n, c in zip(xran, line, line2):
                    screen.addstr(y, x, chars[n], attrs[c])

        elif key == curses.KEY_MOUSE:
            did, x, y, z, button = curses.getmouse()
            x = x//2*2

            count += 1
            ymax, xmax = screen.getmaxyx()
            screen.addstr(ymax-1, 0, f"{spins[count%len(spins)]}({x: 04d},{y: 04d}) {button:09_X}")

            if button & curses.BUTTON2_PRESSED or button & BUTTON13_PRESSED and (x, y) == (0, 0):
                check1, check2 = check2, check1
                screen.addstr(0, 0, "F", attrs[check1])
                screen.addstr(0, 1, "B", attrs[check2])

            elif button == 0 or button & BUTTON_DRAG or button & BUTTON13_PRESSED:
                if button & curses.BUTTON1_PRESSED:
                    check = check1
                elif button & curses.BUTTON3_PRESSED:
                    check = check2

                ch = "　"
                if y in yran and x in xran:
                    i, j = (x-2)//2, y-2
                    chk[j][i] = check
                    n = pzl[j][i]
                    ch = chars[n]

                screen.addstr(y, x, ch, attrs[check])

finally:
    print("\033[?1002l\n")
    curses.endwin()
    curses.flushinp()

