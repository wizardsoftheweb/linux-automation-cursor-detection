#!/usr/bin/env python
"""This file demonstrates color snooping with Xlib"""
from __future__ import print_function

from os import getenv
import time

from Xlib.display import Display
from Xlib.X import ZPixmap

# Pull display from environment
DISPLAY_NUM = getenv('DISPLAY')
# Activate discovered display (or default)
DISPLAY = Display(DISPLAY_NUM)
# Specify the display's screen for convenience
SCREEN = DISPLAY.screen()
# Specify the base element
ROOT = SCREEN.root
# Store width and height
ROOT_GEOMETRY = ROOT.get_geometry()

# Ensure we can run this
EXTENSION_INFO = DISPLAY.query_extension('XInputExtension')

START = time.time()
COORDS = ROOT.query_pointer()
# Create an X dump at the coordinate we want
DISPLAY_IMAGE = ROOT.get_image(
    x=COORDS.root_x,
    y=COORDS.root_y,
    width=1,
    height=1,
    format=ZPixmap,
    plane_mask=int("0xFFFFFF", 16)
)
# Strip its color info
PIXEL = getattr(DISPLAY_IMAGE, 'data')
# Look up the color
RESULTS = SCREEN.default_colormap.query_colors(PIXEL)
# If there are multiple, just return the last one
for raw_color in RESULTS:
    final = (
        raw_color.red,
        raw_color.green,
        raw_color.blue
    )
print("RGB: (%d,%d,%d)" % (final[0] / 256, final[1] / 256, final[2] / 256))
print("Mouse: (%d,%d)" % (COORDS.root_x, COORDS.root_y))
END = time.time()
print("Start: %s" % (START))
print("End: %s" % (END))
print("Difference: %s" % (END - START))
