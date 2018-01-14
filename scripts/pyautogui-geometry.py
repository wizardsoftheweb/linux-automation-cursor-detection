"""This file illustrates a basic pyautogui setup"""

from __future__ import print_function
import time

import pyautogui

START = time.time()
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
MOUSE_X, MOUSE_Y = pyautogui.position()
END = time.time()

print("Screen: %dx%d" % (SCREEN_WIDTH, SCREEN_HEIGHT))
print("Mouse: (%d,%d)" % (MOUSE_X, MOUSE_Y))
print("Start: %s" % (START))
print("End: %s" % (END))
print("Difference: %s" % (END - START))
