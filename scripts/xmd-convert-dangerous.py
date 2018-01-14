"""This file contains code to monitor the desktop environment"""
from __future__ import print_function

import subprocess
import time

START = time.time()
OUTPUT = subprocess.check_output(
    'eval $(xdotool getmouselocation --shell); '
    'xwd -root -screen -silent '
    '| convert xwd:- -crop "1x1+$X+$Y" text:-',
    shell=True
)
END = time.time()
print(OUTPUT)
print("START: %s" % (START))
print("End: %s" % (END))
print("Difference: %s" % (END - START))
