"""This file runs several commands without allowing them to communicate directly`"""

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

COMPILED_PATTERN = re.compile(FULL_XDO_PATTERN, re.VERBOSE | re.MULTILINE)

START = time.time()
COORD = subprocess.check_output([
    'xdotool',
    'getmouselocation',
    '--shell'
])
MATCHED = COMPILED_PATTERN.match(COORD)
DUMP = subprocess.check_output([
    'xwd',
    '-root',    # starts from the base up
    '-screen',  # snags the visible screen for things like menus
    '-silent',  # don't alert
    '-out',     # outfile
    'dump.xwd'
])
IMAGE = subprocess.check_output([
    'convert',
    'dump.xwd',  # infile
    '-crop',    # restrict the image to the cursor
    '1x1+%s+%s' % (MATCHED.group('x'), MATCHED.group('y')),
    'text:-'    # throw out on stdout
])
END = time.time()

print COORD
print IMAGE
print "Start: %s" % (START)
print "End: %s" % (END)
print "Difference: %s" % (END - START)
