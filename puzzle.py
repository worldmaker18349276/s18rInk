import curses

try:
    screen = curses.initscr()
    screen.keypad(1)
    curses.curs_set(0)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.mouseinterval(10)
    print("\033[?1003h\n")
    curses.flushinp()
    curses.noecho()
    screen.clear()

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    BUTTON1_RELEASED = curses.BUTTON1_RELEASED # 0x0001
    BUTTON1_PRESSED  = curses.BUTTON1_PRESSED  # 0x0002
    BUTTON1_CLICKED  = curses.BUTTON1_CLICKED  # 0x0004
    BUTTON_CTRL  = curses.BUTTON_CTRL  # 0x0200_0000
    BUTTON_SHIFT = curses.BUTTON_SHIFT # 0x0400_0000
    BUTTON_ALT   = curses.BUTTON_ALT   # 0x0800_0000
    BUTTON_SCROLLUP   = 0x0001_0000
    BUTTON_SCROLLDOWN = 0x0020_0000
    BUTTON_DRAG       = 0x1000_0000

    nums = {".":-1, "0":0, "1":1, "2":2, "3":3, "4":4}
    chars = ["０", "１", "２", "３", "４", "　"]
    attrs = {None: curses.color_pair(1),
             False: curses.color_pair(2),
             True: curses.color_pair(2) | curses.A_REVERSE,
             }
    with open("test") as f:
        pzl_str = f.read()
    pzl = [[nums[ch] for ch in line] for line in pzl_str.strip().split("\n")]
    chk = [[None for n in line] for line in pzl]
    chk_ = [[c for c in line] for line in chk]

    yran = range(2, len(pzl)+2, 1)
    xran = range(2, len(pzl[0])*2+2, 2)
    for y, line, line2 in zip(yran, pzl, chk):
        for x, n, c in zip(xran, line, line2):
            screen.addstr(y, x, chars[n], attrs[c])

    check = True
    screen.addstr(0, 0, "Ｏ", attrs[check])

    count = 0
    spins = ["◴ ", "◵ ", "◶ ", "◷ "]

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
            screen.addstr(ymax-1, 0, f"{spins[count%len(spins)]}{did},{x:0>3d},{y:0>3d},{z},{button:0>8X}")

            if button & BUTTON_SCROLLDOWN and (y == 0) <= (x == 0):
                check = True
                screen.addstr(0, 0, "Ｏ", attrs[check])

            elif button & BUTTON_SCROLLUP and (y == 0) <= (x == 0):
                check = False
                screen.addstr(0, 0, "Ｏ", attrs[check])

            elif x == 0 and y == 0:
                check = None
                screen.addstr(0, 0, "Ｏ", attrs[check])
                
            elif button & BUTTON_DRAG:
                value = check if not bool(button & BUTTON_CTRL) else None
                ch = "　"
                if y in yran and x in xran:
                    i, j = (x-2)//2, y-2
                    chk[j][i] = value
                    n = pzl[j][i]
                    ch = chars[n]

                screen.addstr(y, x, ch, attrs[value])

finally:
    print("\033[?1003l\n")
    curses.endwin()
    curses.flushinp()

