# coding: utf-8

import time, random, os, sys, Getch

VIM_KEYS = False

def xyToBashCoords(x,y):
        return "\033[" + str(y + 1) + ";" + str(x) + "H"

def addPos(pos1, pos2):
        return [pos1[i] + pos2[i] for i in range(len(pos1))]

levelNum = 0

userInput = " "

KEY_UP      = "w"
KEY_DOWN    = "s"
KEY_LEFT    = "a"
KEY_RIGHT   = "d"

KEY_P_1_UP    = "i"
KEY_P_1_LEFT  = "j"
KEY_P_1_DOWN  = "k"
KEY_P_1_RIGHT = "l"

KEY_P_2_UP    = "I"
KEY_P_2_LEFT  = "J"
KEY_P_2_DOWN  = "K"
KEY_P_2_RIGHT = "L"

# TODO: update portal information
def print_usage():
    print """\
Usage:
    python %s [-vh] [-l <level>]

Options:
    -v          Use VIM key bindings instead of normal keys
    -l <level>  Start on that level. <level> starts at 0

Keys:
    Normal key bindings:
        w       Go up
        s       Go down
        a       Go left
        d       Go right

        i       Shoot blue portal up
        k       Shoot blue portal down
        j       Shoot blue portal left
        l       Shoot blue portal right
        I       Shoot red portal up
        K       Shoot red portal down
        J       Shoot red portal left
        L       Shoot red portal right

        r       Restart level
        b       Previous level
        n       Next level

    Vim key bindings:
        h       Go left
        j       Go down
        k       Go up
        l       Go right

        w       Shoot blue portal up
        s       Shoot blue portal down
        a       Shoot blue portal left
        d       Shoot blue portal right
        W       Shoot red portal up
        S       Shoot red portal down
        A       Shoot red portal left
        D       Shoot red portal right

        r       Restart level
        b       Previuos level (back)
        n       Next level
""" % __file__

last_arg = ""
for arg in sys.argv:
    if arg[0] == "-":
        last_arg = ""
        if arg == "-v":
            VIM_KEYS = True
        elif arg == "-h":
            print_usage()
            sys.exit()
        else:
            last_arg = arg
    else:
        if last_arg == "-l":
            levelNum = int(arg)
        last_arg = ""

if VIM_KEYS:
    KEY_UP      = "k"
    KEY_DOWN    = "j"
    KEY_LEFT    = "h"
    KEY_RIGHT   = "l"

    KEY_P_1_UP    = "w"
    KEY_P_1_DOWN  = "s"
    KEY_P_1_LEFT  = "a"
    KEY_P_1_RIGHT = "d"

    KEY_P_2_UP    = "W"
    KEY_P_2_DOWN  = "S"
    KEY_P_2_LEFT  = "A"
    KEY_P_2_RIGHT = "D"

portalColors = [123, 100, 255]

try:
    Getch.start()
    while True:
        levelPath = "Levels/level" + str(levelNum) + ".lvl"
        if not os.path.isfile(levelPath): # We have finished the last level.
            break
        level = map(lambda x: list(x[:-1]), open(levelPath, "r").readlines())

        maxLen = max(map(len, level))
        level = [line + [" "] * (maxLen - len(line)) for line in level]

        # Positions indexed by [y, x]
        playerPos = [1, 1] # Default pos
        currentDir = [1, 0]

        hasPortalGun = None
        portalGunAngle = 0 # 0 = Up, 1 = Up/Right, 2 = Right etc.

        for y, line in enumerate(level):
	    for x, ch in enumerate(line):
		if ch == "@":
		    level[y][x] = " "
		    playerPos = [y, x]

        changedGravityTime = 0
        changedGravityDir = " "
        changedGravityParticles = []

        lastPortalMove = [] # [x, y]
        lastPortalTime = -1

        portalGunPortals = [[-1, -1], [-1, -1]] # [y, x]
        portalShootings = [] # [y, x, vy, vx, num]

        nextArrow = False # REMOVE!

        while 1:
	    # Clear screen

	    print "\033[2J"
	    if levelNum == 0:
		print "To see how to move and other stuff, run this program with -h."

	    # Print map
	    for y, line in enumerate(level):
		    printLine = "" # Current line that is going to be printed
		    for x, ch in enumerate(line):
			printChr = " " # Current char
			color = "\033[0m" # Default
			if playerPos == [y, x]:
			    printChr = "@"
			    color = "\033[38;5;1m\033[1m"
			else:
			    printChr = ch
			    if ch in "<>^v":
				color = "\033[38;5;4m\033[1m"
			    if ch == "*":
				color = "\033[38;5;11m\033[48;5;11m"
			    if ch == "#":
				color = "\033[38;5;2m\033[48;5;2m"
			    if ch == "X":
				color = "\033[38;5;1m"
			if ch in "-_/|h":
			    color += "\033[38;5;1m"
			    if ch == "_":
				color += "\033[4m"

			for particle in changedGravityParticles:
			    if printChr == " " and particle[0] == y and particle[1] == x:
				printChr = "-|"[changedGravityDir in "^v"]
			if ch.isdigit():
			    color = "\033[38;5;" + ch + "m"
			    printChr = "O"
			if lastPortalTime < 3:
			    for portal in lastPortalMove:
				if portal == [y, x]:
				    color += "\033[1m"
			for i, portal in enumerate(portalShootings):
			    if portal[0] == y and portal[1] == x:
				printChr = "0"
				color = "\033[38;5;%im" % portalColors[portal[4]]

			for i, portal in enumerate(portalGunPortals):
			    if portal == [y, x]:
				printChr = "0"
				color = "\033[38;5;%im" % portalColors[i]

			printLine += "\033[" + str(y + 1) + ";" + str(x + 1) + "H\033[0m" + color + printChr

		    print printLine + "\033[0m "
	    for y in range(len(level)):
		for x in range(len(level[y])):
		    if level[y][x] == "#":
			print "\033[" + str(y) + ";" + str(x + 1) + "H"
			break
	    if [-1, -1] not in portalGunPortals:
		if playerPos == portalGunPortals[0]:
		    playerPos = portalGunPortals[1]
		elif playerPos == portalGunPortals[1]:
		    playerPos = portalGunPortals[0]
		if playerPos in portalGunPortals:
		    # We have teleported
		    for direction in [currentDir, [0, 1], [1, 0], [0, -1], [-1, 0]]:
			newPos = addPos(playerPos, direction)
			if level[newPos[0]][newPos[1]] != "#":
			    playerPos = newPos
			    break

	    for i, particle in enumerate(changedGravityParticles):
		changedGravityParticles[i] = addPos(particle, currentDir)
	    while changedGravityTime > 3 and random.randint(0, 2) == 0 and len(changedGravityParticles):
		changedGravityParticles.pop()

	    changedGravityTime += 1
	    lastPortalTime += 1

	    playerPosChr = level[playerPos[0]][playerPos[1]]
	    if playerPosChr in ">^<v":
		if playerPosChr == ">":
		    newDir = [0, 1]
		if playerPosChr == "^":
		    newDir = [-1, 0]
		if playerPosChr == "<":
		    newDir = [0, -1]
		if playerPosChr == "v":
		    newDir = [1, 0]
		if newDir != currentDir:
		    currentDir = newDir
		    changedGravityTime = 0
		    changedGravityDir = playerPosChr
		    while len(changedGravityParticles) < 5:
			changedGravityParticles.append([random.randrange(0, len(level)), random.randrange(0, len(level[0]))])
	    if playerPosChr == "*":
		break
	    if playerPosChr == "=":
		hasPortalGun = True
		level[playerPos[0]][playerPos[1]] = " "
	    for y in range(len(level)):
		for x in range(len(level[y])):
			if level[y][x] == "/":
				level[y][x] = "_"
	    if playerPosChr == "-":
		level[playerPos[0]][playerPos[1]] = "_"
		for y in range(len(level)):
			for x in range(len(level[y])):
				if level[y][x] == "|":
					level[y][x] = "/"
	    if playerPosChr.isdigit():
		allPortals = []
		for y in range(len(level)):
		    for x in range(len(level[y])):
			if level[y][x] == playerPosChr:
			    allPortals.append([y, x])
		lastPortalMove = [playerPos]
		lastPortalTime = 0
		if len(allPortals) == 2:
		    playerPos = allPortals[allPortals.index(playerPos) - 1]
		else:
		    playerPos = allPortals[0]
		lastPortalMove.append(playerPos)

	    falling = True
	    fallingPos = addPos(playerPos, currentDir)
	    fallingPosChr = level[fallingPos[0]][fallingPos[1]]
	    if fallingPosChr in "|#":
		fallingPos = playerPos
		falling = False
	    playerPos = fallingPos

	    newPortalShooting = []
	    for portal in portalShootings:
		newPos = [portal[0] + portal[2], portal[1] + portal[3]]
		if level[newPos[0]][newPos[1]] == "#":
		    portalGunPortals[portal[4]] = portal[:2]
		else:
		    newPortalShooting.append([newPos[0], newPos[1], portal[2], portal[3], portal[4]])
	    portalShootings = newPortalShooting

	    time.sleep(0.1)
	    if len(Getch.keyQueue):
		userInput = Getch.keyQueue.pop()
		if userInput == "\x03": # Ctrl+C
		    exit()
		moving = [0, 0]
		if not falling:
		    if userInput == KEY_UP:
			moving = [-1, 0]
		    if userInput == KEY_LEFT:
			moving = [0, -1]
		    if userInput == KEY_DOWN:
			moving = [1, 0]
		    if userInput == KEY_RIGHT:
			moving = [0, 1]
		if userInput == "r":
		    levelNum -= 1
		    break
		if userInput == "b":
		    levelNum -= 2
		    break
		if userInput == "n":
		    break
		if hasPortalGun:
		    if userInput == KEY_P_1_UP:
			portalShootings.append([playerPos[0], playerPos[1], -1, 0, 0])
		    if userInput == KEY_P_1_RIGHT:
			portalShootings.append([playerPos[0], playerPos[1], 0, 1, 0])
		    if userInput == KEY_P_1_DOWN:
			portalShootings.append([playerPos[0], playerPos[1], 1, 0, 0])
		    if userInput == KEY_P_1_LEFT:
			portalShootings.append([playerPos[0], playerPos[1], 0, -1, 0])
		    if userInput == KEY_P_2_UP:
			portalShootings.append([playerPos[0], playerPos[1], -1, 0, 1])
		    if userInput == KEY_P_2_RIGHT:
			portalShootings.append([playerPos[0], playerPos[1], 0, 1, 1])
		    if userInput == KEY_P_2_DOWN:
			portalShootings.append([playerPos[0], playerPos[1], 1, 0, 1])
		    if userInput == KEY_P_2_LEFT:
			portalShootings.append([playerPos[0], playerPos[1], 0, -1, 1])
		    if userInput == "c":
			portalGunPortals = [[-1, -1], [-1, -1]]
		movingPos = addPos(playerPos, moving)
		if level[movingPos[0]][movingPos[1]] in "|#":
		    movingPos = playerPos
		playerPos = movingPos
	    else:
		if len(Getch.keyQueue) > 0:
		    key = Getch.keyQueue.pop()
		    if key == "\x03": # Ctrl-C
			exit()


        print "\033[2J\033[0;0H" + ["Very Good!", "Very good", "very good", "voru good", u"VAEIRY GÜD", "gj", "good job", u"V̪͎̯͇̝̫̗Ḙ̮̤̹̞R̵̹̗͖Ỵ̠̰̯̗͙̤͘ ͏͎̝͚̬̥̙͇G̴͍͉̮̤O҉̻̳͓O͈̠̞D"][levelNum % 8]

        levelNum += 1
        time.sleep(1)

    # Clear screen at the end
    print "\033[2J"
    os.system("reset")
except:
    os.system("reset")
    print("An error occured")