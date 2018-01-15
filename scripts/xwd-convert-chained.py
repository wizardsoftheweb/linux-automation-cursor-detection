#!/usr/bin/env python
"""This file runs several commands by linking stdout and stdin in subprocesses"""
from __future__ import print_function

import re
import subprocess
import time

FULL_XDO_PATTERN = r"""
^\s*X=(?P<x>\d+)    # Name x for easy access
\s+
Y=(?P<y>\d+)        # Name y for easy access
\s+
[\s\S]+$            # Ditch everything else
"""

COMPILED_XDO_PATTERN = re.compile(FULL_XDO_PATTERN, re.VERBOSE | re.MULTILINE)

FULL_RGB_PATTERN = r"""
^[\s\S]*?
0,0:\s*\(\s*(?P<rgb>
\d+,\s*
\d+,\s*
\d+
)\s*
\).*$
"""

COMPILED_RGB_PATTERN = re.compile(FULL_RGB_PATTERN, re.VERBOSE | re.MULTILINE)

START = time.time()
COORD = subprocess.check_output([
    'xdotool',
    'getmouselocation',
    '--shell'
])
MATCHED = COMPILED_XDO_PATTERN.match(COORD)
IMAGE = subprocess.Popen(
    [
        'convert',
        'xwd:-',
        '-crop',    # restrict the image to the cursor
        '1x1+%s+%s' % (MATCHED.group('x'), MATCHED.group('y')),
        'text:-'    # throw out on stdout
    ],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
)
DUMP = subprocess.Popen(
    [
        'xwd',
        '-root',    # starts from the base up
        '-screen',  # snags the visible screen for things like menus
        '-silent',  # don't alert
    ],
    stdout=IMAGE.stdin
)
OUTPUT = IMAGE.communicate()[0]
DUMP.wait()
RGB = COMPILED_RGB_PATTERN.match(OUTPUT)
SIMPLE_RGB = [int(x) / 256 for x in RGB.group('rgb').split(',')]
print("RGB: (%d,%d,%d)" % (SIMPLE_RGB[0], SIMPLE_RGB[1], SIMPLE_RGB[2]))
print("Mouse: (%s,%s)" % (MATCHED.group('x'), MATCHED.group('y')))
END = time.time()

print("Start: %s" % (START))
print("End: %s" % (END))
print("Difference: %s" % (END - START))
