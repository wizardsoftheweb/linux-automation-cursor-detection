"""This file runs several commands by linking stdout and stdin in subprocesses"""
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
END = time.time()

print OUTPUT
print "Start: %s" % (START)
print "End: %s" % (END)
print "Difference: %s" % (END - START)
