"""This file demonstrates color snooping with Xlib"""
from __future__ import print_function

from os import getenv
import time

from Xlib.display import Display
from Xlib.ext import xinput
from Xlib.X import ZPixmap

# Pull display from environment
DISPLAY_NUM = getenv("DISPLAY")
# Activate discovered display (or default)
DISPLAY = Display(DISPLAY_NUM)
# Specify the display's screen for convenience
SCREEN = DISPLAY.screen()
# Specify the base element
ROOT = SCREEN.root
# Store width and height
ROOT_GEOMETRY = ROOT.get_geometry()


def get_color(event):
    """Snags the color under the cursor"""
    start = time.time()
    # Create an X dump at the coordinate we want
    display_image = ROOT.get_image(
        x=event.data.root_x,
        y=event.data.root_y,
        width=1,
        height=1,
        format=ZPixmap,
        plane_mask=int("0xFFFFFF", 16)
    )
    # Strip its color info
    pixel = getattr(display_image, 'data')
    # Look up the color
    results = SCREEN.default_colormap.query_colors(pixel)
    # If there are multiple, just return the last one
    for raw_color in results:
        final = (
            raw_color.red,
            raw_color.green,
            raw_color.blue
        )
    end = time.time()
    print('#%04x%04x%04x' % (final[0], final[1], final[2]))
    print("Start: %s" % (start))
    print("End: %s" % (end))
    print("Difference: %s" % (end - start))

# This is a simplified version of the xinput example
# https://github.com/python-xlib/python-xlib/blob/b73b17d6d3f0d30da36490d3b59bc2a98309f2a6/examples/xinput.py#L59
# The most recent version may or may not match line numbers
# https://github.com/python-xlib/python-xlib/blob/master/examples/xinput.py#L59
try:
    # Ensure we can run this
    EXTENSION_INFO = DISPLAY.query_extension('XInputExtension')
    # Call out flag
    XINPUT_MAJOR = EXTENSION_INFO.major_opcode

    # Listen for movement on the root device
    ROOT.xinput_select_events([
        (xinput.AllDevices, xinput.MotionMask),
    ])

    # Loop control
    ACTIVE = True

    while ACTIVE:
        # Check the next event
        EVENT = DISPLAY.next_event()
        if (
                EVENT.type == DISPLAY.extension_event.GenericEvent
                and
                EVENT.extension == XINPUT_MAJOR
        ):
            # Snag the color
            get_color(EVENT)
            # Kill the loop
            ACTIVE = False
# Give ctrl+c an easy out
except KeyboardInterrupt:
    pass
