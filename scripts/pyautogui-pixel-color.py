#!/usr/bin/env python
"""This file illustrates using pyautogui to check a pixel's color"""
from __future__ import print_function

import time

import pyautogui

START = time.time()
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
MOUSE_X, MOUSE_Y = pyautogui.position()
PIXEL = pyautogui.screenshot(
    region=(
        MOUSE_X, MOUSE_Y, 1, 1
    )
)
COLOR = PIXEL.getcolors()
END = time.time()

print("Screen: %dx%d" % (SCREEN_WIDTH, SCREEN_HEIGHT))
print("Mouse: (%d,%d)" % (MOUSE_X, MOUSE_Y))
print("RGB: %s" % (COLOR[0][1].__str__()))
print("Start: %s" % (START))
print("End: %s" % (END))
print("Difference: %s" % (END - START))
