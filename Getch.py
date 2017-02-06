import threading, time

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

getch = _Getch()

def _background():
	while True:
		keyQueue.append(getch())
		time.sleep(0.1)

keyQueue = []
def start():
	t = threading.Thread(target = _background)
	t.daemon = True
	t.start()


if __name__ == "__main__":
    start()
    print("\033[2J")
    i = 0
    while True:
            i += 1
            print("\033[" + str(i) + ";0H" + str(i), keyQueue)
            time.sleep(0.1)


