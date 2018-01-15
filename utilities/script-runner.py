# pylint: disable=misplaced-comparison-constant
# pylint: disable=too-many-arguments
"""This file runs the provided scripts many times to collect data"""
from __future__ import print_function

from csv import writer, QUOTE_NONNUMERIC
from os.path import dirname, isfile, join, splitext
from random import randrange, seed
from re import compile as re_compile, MULTILINE, search, VERBOSE
from subprocess import check_output
from sys import exit as sys_exit, stderr
from time import sleep, time as unix_time

import logging

from promise import Promise

import pyautogui

# Easy defaults
DEFAULT_SEED = 47
RUN_COUNT = 100

# Start with proper screen info
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Directory info
LOCATION = dirname(__file__)

# Scripts to hit and their location
SCRIPTS_PATH = join(LOCATION, '..', 'scripts')
SCRIPTS_TO_TEST = [
    'pyautogui-pixel-color.py',
    'xlib-color.py',
    'xwd-convert-chained.py',
    'xwd-convert.sh',
]

# Main CSV output
DATA_FILE_NAME = join(
    'data',
    'run_time_comparison.csv',
)

# Attach a logger
LOGGER = logging.getLogger('script-runner')
CONSOLE_HANDLER = logging.StreamHandler(stream=stderr)
CONSOLE_FORMATTER = logging.Formatter(
    '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
)
CONSOLE_HANDLER.setFormatter(CONSOLE_FORMATTER)
LOGGER.addHandler(CONSOLE_HANDLER)
# I haven't wanted to argparser yet, so this logs everything
LOGGER.setLevel(logging.DEBUG)

# Create an empty list to hold the points we'll hit
POINTS = list()


def write_data(script_name, run_time, red, green, blue, x_coordinate, y_coordinate, finished=None):
    """Given a row data, writes it to the main CSV"""
    LOGGER.info('Writing data to file')
    with open(DATA_FILE_NAME, 'a') as log_file:
        log_writer = writer(
            log_file,
            delimiter=',',
            quotechar='"',
            quoting=QUOTE_NONNUMERIC
        )
        # Attach a final timestamp if not already there
        if finished is None:
            finished = unix_time()
        log_writer.writerow(
            [
                script_name,
                run_time,
                red,
                green,
                blue,
                x_coordinate,
                y_coordinate,
                finished
            ]
        )
        LOGGER.debug('Write successful')
        return Promise.resolve('written')
    LOGGER.error('Write failed')
    return Promise.reject('Unable to write data')


def bootstrap():
    """Creates the initial application state"""
    LOGGER.debug('Seeding random')
    seed(DEFAULT_SEED)
    # Creates RUN_COUNT many (x,y) points
    get_all_random_points()
    # Create the main data file if it DNE
    if not isfile(DATA_FILE_NAME):
        LOGGER.info('Creating data file')
        return Promise.resolve(
            write_data(
                'script_name',
                'run_time',
                'red',
                'green',
                'blue',
                'x_coordinate',
                'y_coordinate',
                'finished'
            )
        )
    return Promise.resolve('booted')


def get_random_point():
    """Returns a random coordinate on the screen"""
    LOGGER.debug('Creating random point')
    return randrange(0, SCREEN_WIDTH), randrange(400, 1400)


def get_all_random_points():
    """Gets all the random points necessary to run"""
    for _ in range(RUN_COUNT):
        x_coordinate, y_coordinate = get_random_point()
        POINTS.append([x_coordinate, y_coordinate])


def move_mouse_to_specific_location(x_coordinate, y_coordinate):
    """Moves the mouse to a specific point"""
    LOGGER.debug("Moving mouse to (%d,%d)", x_coordinate, y_coordinate)
    pyautogui.moveTo(x_coordinate, y_coordinate)
    return Promise.resolve((x_coordinate, y_coordinate))


def move_mouse_to_random_location(delay=0):
    """Moves the mouse to a new location after a possible delay"""
    LOGGER.info("Sleeping mouse movement for %ds", delay)
    sleep(delay)
    x_coordinate, y_coordinate = get_random_point()
    return Promise.resolve(move_mouse_to_specific_location(x_coordinate, y_coordinate))

# Each script should put out these items in this order (loosely)
FULL_STDOUT_PATTERN = r"""
^[\s\S]*?
RGB:\s+\((?P<rgb>\s*\d+,\s*\d+,\s*\d+)\)
[\s\S]*?
Mouse:\s+\((?P<mouse>\s*\d+,\s*\d+\s*)\)
[\s\S]*?
Difference:\s+(?P<diff>[\d.]+)
[\s\S]*?$
"""

# Compile it for convenience
COMPILED_STDOUT_PATTERN = re_compile(FULL_STDOUT_PATTERN, VERBOSE | MULTILINE)


def parse_out_data(haystack):
    """Finds the result from stdout"""
    LOGGER.info('Parsing stdout')
    possible_result = search(COMPILED_STDOUT_PATTERN, haystack)
    if possible_result.group('diff'):
        LOGGER.debug("Diff: %f", float(possible_result.group('diff')))
        if possible_result.group('rgb'):
            raw_rgb = map(int, possible_result.group('rgb').split(','))
            LOGGER.debug("RGB: (%d,%d,%d)", *raw_rgb)
            if possible_result.group('mouse'):
                mouse_coords = map(
                    int, possible_result.group('mouse').split(',')
                )
                LOGGER.debug("Mouse: (%d,%d)", *mouse_coords)
                return Promise.resolve(
                    [float(possible_result.group('diff'))]
                    + raw_rgb
                    + mouse_coords
                )
            LOGGER.error('Parsing failed')
            return Promise.reject('Mouse not found')
        LOGGER.error('Parsing failed')
        return Promise.reject('RGB not found')
    LOGGER.error('Parsing failed')
    return Promise.reject('Difference not found')


def execute_script(script_name):
    """Runs the given script"""
    full_script_path = join(SCRIPTS_PATH, script_name)
    if isfile(full_script_path):
        extension = splitext(script_name)
        runner = (
            'python'
            if '.py' == extension[1]
            else 'bash'
        )
        LOGGER.debug("%s %s", runner, full_script_path)
        result = '\n\n' + check_output([runner, full_script_path])
        LOGGER.debug(result)
        return Promise(
            lambda resolve, reject: resolve(parse_out_data(result))
        ).then(
            lambda result: Promise.resolve(
                [
                    result[0] * (
                        1000
                        if extension[1] == '.py'
                        else 1
                    )
                ] + result[1:]
            )
        )
    LOGGER.error("%s failed", script_name)
    return Promise.reject("%s failed" % (script_name))


def test_single_script_once(script_name):
    """Tests a single script"""
    LOGGER.debug("Running full promise for %s", script_name)
    return Promise.resolve(
        execute_script(script_name)
    ).then(
        lambda result: Promise.resolve(
            [script_name] + result
        )
    ).then(lambda result: Promise.resolve(write_data(*result)))


def full_run_single_script(script_name, list_of_points):
    """Runs a single script over all the points"""
    if not list_of_points:
        return Promise.resolve('finished')
    point = list_of_points.pop()
    return Promise.resolve(
        move_mouse_to_specific_location(*point)
    ).then(
        Promise.resolve(
            test_single_script_once(script_name)
        )
    ).then(
        lambda result: full_run_single_script(script_name, list_of_points),
        lambda result: full_run_single_script(
            script_name,
            list_of_points + [point]
        )
    )


def full_run_all_the_scripts(scripts_to_test):
    """Runs each script completely before moving on"""
    if not scripts_to_test:
        return Promise.resolve('finished')
    LOGGER.debug('Pausing for X Window')
    sleep(5)
    script_name = scripts_to_test.pop()
    return Promise.resolve(
        full_run_single_script(script_name, POINTS[:])
    ).then(
        lambda result: full_run_all_the_scripts(scripts_to_test)
    )


def cli():
    """Main CLI runner"""
    bootstrap().then(
        lambda result: full_run_all_the_scripts(SCRIPTS_TO_TEST[:])
    )

if '__main__' == __name__:
    LOGGER.info("CLI assumed")
    sys_exit(cli())
