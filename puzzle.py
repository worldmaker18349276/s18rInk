import curses

use_unicode = True
puzzle_str = """
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
    symbols = ["０", "１", "２", "３", "４", "　"]
    spins = ["◴ ", "◵ ", "◶ ", "◷ "]
else:
    symbols = [" 0", " 1", " 2", " 3", " 4", "  "]
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
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_CYAN)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_MAGENTA)
    screen.bkgd(" ", curses.color_pair(1))

    BUTTON_SCROLLUP   = 0x0001_0000
    BUTTON_SCROLLDOWN = 0x0020_0000
    BUTTON_SCROLL     = BUTTON_SCROLLUP | BUTTON_SCROLLDOWN
    BUTTON_DRAG       = 0x1000_0000
    BUTTON13_PRESSED  = curses.BUTTON1_PRESSED | curses.BUTTON3_PRESSED

    nums = {".":-1, "0":0, "1":1, "2":2, "3":3, "4":4}
    attrs = [curses.color_pair(1),
             curses.color_pair(1) | curses.A_REVERSE,
             curses.color_pair(2),
             curses.color_pair(2) | curses.A_REVERSE,
             curses.color_pair(3),
             curses.color_pair(3) | curses.A_REVERSE,
             curses.color_pair(4),
             curses.color_pair(4) | curses.A_REVERSE,
             ]

    puzzle = [[nums[ch] for ch in line] for line in puzzle_str.strip().split()]
    checks = [[0 for n in line] for line in puzzle]
    checks_ = [[c for c in line] for line in checks]

    width, height = len(puzzle[0]), len(puzzle)
    yran = range(2, height+2, 1)
    xran = range(2, width*2+2, 2)
    for y, line, line2 in zip(yran, puzzle, checks):
        for x, n, c in zip(xran, line, line2):
            screen.addstr(y, x, symbols[n], attrs[c])

    count = 0
    check1 = 1
    check2 = 0
    check = check1
    screen.addstr(0, 0, "F", attrs[check1])
    screen.addstr(0, 1, "B", attrs[check2])

    cran = range(4, 20, 2)
    for x, checki in zip(cran, range(8)):
        screen.addstr(0, x, f"{checki: 2d}", attrs[checki])

    while True:
        key = screen.getch()
        if key == 27:
            break

        elif key == ord("x"):
            checks_ = [[c for c in line] for line in checks]

        elif key == ord("z"):
            checks = [[c for c in line] for line in checks_]

            for y, line, line2 in zip(yran, puzzle, checks):
                for x, n, c in zip(xran, line, line2):
                    screen.addstr(y, x, symbols[n], attrs[c])

        elif key == curses.KEY_MOUSE:
            did, x, y, z, button = curses.getmouse()
            x = x//2*2

            count += 1
            ymax, xmax = screen.getmaxyx()
            screen.addstr(ymax-1, 0, f"{spins[count%len(spins)]}({x: 04d},{y: 04d}) {button:09_X}")

            if button & BUTTON_SCROLL:
                if button & BUTTON_SCROLLDOWN:
                    check1 = min(check1+1, len(cran)-1)
                elif button & BUTTON_SCROLLUP:
                    check1 = max(check1-1, 0)

            elif button & curses.BUTTON2_PRESSED:
                if y in yran and x in xran:
                    i, j = xran.index(x), yran.index(y)
                    check1 = checks[j][i]
                elif y == 0 and x in cran:
                    check1 = cran.index(x)
                else:
                    check1 = 1

            elif button & BUTTON13_PRESSED and y == 0 and x in cran:
                if button & curses.BUTTON1_PRESSED:
                    check1 = cran.index(x)
                elif button & curses.BUTTON3_PRESSED:
                    check2 = cran.index(x)

            elif button & BUTTON13_PRESSED and (x, y) == (0, 0):
                check1, check2 = check2, check1

            elif button & BUTTON13_PRESSED and button & curses.BUTTON_CTRL and y in yran and x in xran:
                if button & curses.BUTTON1_PRESSED:
                    check = check1
                elif button & curses.BUTTON3_PRESSED:
                    check = check2

                i, j = xran.index(x), yran.index(y)
                orig = checks[j][i]

                fillin = [(i, j)]
                for i, j in fillin:
                    for i_, j_ in [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]:
                        if (i_, j_) in fillin:
                            continue
                        if i_ in range(width) and j_ in range(height) and checks[j_][i_] == orig:
                            fillin.append((i_, j_))

                for i, j in fillin:
                    x, y = xran[i], yran[j]
                    checks[j][i] = check
                    sym = symbols[puzzle[j][i]]
                    screen.addstr(y, x, sym, attrs[check])

            elif (button & BUTTON13_PRESSED or button & BUTTON_DRAG or button == 0) and y in yran and x in xran:
                if button & curses.BUTTON1_PRESSED:
                    check = check1
                elif button & curses.BUTTON3_PRESSED:
                    check = check2

                i, j = xran.index(x), yran.index(y)
                checks[j][i] = check
                sym = symbols[puzzle[j][i]]
                screen.addstr(y, x, sym, attrs[check])

            screen.addstr(0, 0, "F", attrs[check1])
            screen.addstr(0, 1, "B", attrs[check2])

finally:
    print("\033[?1002l\n")
    curses.endwin()
    curses.flushinp()

