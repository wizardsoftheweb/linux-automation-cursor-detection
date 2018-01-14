"""This file runs several commands without allowing them to communicate directly`"""

import re
import subprocess
import time

FULL_XDO_PATTERN = r"""
^\s*X=(?P<x>\d+)
\s+
Y=(?P<y>\d+)
\s+
[\s\S]+$
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
    '-root',
    '-screen',
    '-silent',
    '-out',
    'dump.xwd'
])
IMAGE = subprocess.check_output([
    'convert',
    'dump.xwd',
    '-crop', '1x1+%s+%s' % (MATCHED.group('x'), MATCHED.group('y')),
    'text:-'
])
END = time.time()

print COORD
print IMAGE
print "Start: %s" % (START)
print "End: %s" % (END)
print "Difference: %s" % (END - START)
