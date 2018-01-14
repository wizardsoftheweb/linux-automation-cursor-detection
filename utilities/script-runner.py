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

DEFAULT_SEED = 47
RUN_COUNT = 2
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
LOCATION = dirname(__file__)
SCRIPTS_PATH = join(LOCATION, '..', 'scripts')

SCRIPTS_TO_TEST = [
    'pyautogui-pixel-color.py',
    'xlib-color.py',
    'xwd-convert-chained.py',
    'xwd-convert.sh',
]

DATA_FILE_NAME = join(
    'data',
    'run_time_comparison.csv',
)

LOGGER = logging.getLogger('script-runner')
CONSOLE_HANDLER = logging.StreamHandler(stream=stderr)
CONSOLE_FORMATTER = logging.Formatter(
    '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
)
CONSOLE_HANDLER.setFormatter(CONSOLE_FORMATTER)
LOGGER.addHandler(CONSOLE_HANDLER)
LOGGER.setLevel(logging.DEBUG)


def write_data(script_name, run_time, red, green, blue, final_x, final_y, finished=None):
    """Log a test row"""
    LOGGER.info('Writing data to file')
    with open(DATA_FILE_NAME, 'a') as log_file:
        log_writer = writer(
            log_file,
            delimiter=',',
            quotechar='"',
            quoting=QUOTE_NONNUMERIC
        )
        if finished is None:
            finished = unix_time()
        log_writer.writerow(
            [script_name, run_time, red, green, blue, final_x, final_y, finished]
        )
        LOGGER.debug('Write successful')
        return Promise.resolve('written')
    LOGGER.error('Write failed')
    return Promise.reject('Unable to write data')


def bootstrap():
    """Creates the initial state"""
    LOGGER.debug('Seeding random')
    seed(DEFAULT_SEED)
    if not isfile(DATA_FILE_NAME):
        LOGGER.info('Creating data file')
        return Promise.resolve(
            write_data(
                'script_name',
                'run_time',
                'red',
                'green',
                'blue',
                'final_x',
                'final_y',
                'finished'
            )
        )
    return Promise.resolve('booted')


def get_random_point():
    """Returns a random coordinate on the screen"""
    LOGGER.debug('Creating random point')
    return randrange(0, SCREEN_WIDTH), randrange(0, SCREEN_HEIGHT)


def move_mouse_to_random_location(delay=0):
    """Moves the mouse to a new location after a possible delay"""
    LOGGER.info("Sleeping mouse movement for %ds", delay)
    sleep(delay)
    LOGGER.debug('Moving mouse')
    x_coordinate, y_coordinate = get_random_point()
    pyautogui.moveTo(x_coordinate, y_coordinate)
    return Promise.resolve((x_coordinate, y_coordinate))

FULL_STDOUT_PATTERN = r"""
^[\s\S]*?
RGB:\s+\((?P<rgb>\s*\d+,\s*\d+,\s*\d+)\)
[\s\S]*?
Mouse:\s+\((?P<mouse>\s*\d+,\s*\d+\s*)\)
[\s\S]*?
Difference:\s+(?P<diff>[\d.]+)
[\s\S]*?$
"""

COMPILED_STDOUT_PATTERN = re_compile(FULL_STDOUT_PATTERN, VERBOSE | MULTILINE)


def parse_out_data(haystack):
    """Finds the result from stdout"""
    LOGGER.info('Parsing stdout')
    possible_result = search(COMPILED_STDOUT_PATTERN, haystack)
    if possible_result.group('diff'):
        LOGGER.debug(possible_result.group('diff'))
        if possible_result.group('rgb'):
            raw_rgb = map(int, possible_result.group('rgb').split(','))
            if possible_result.group('mouse'):
                mouse_coords = map(
                    int, possible_result.group('mouse').split(','))
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
    extension = splitext(script_name)
    full_script_path = join(SCRIPTS_PATH, script_name)
    if isfile(full_script_path):
        runner = (
            'python'
            if '.py' == extension[1]
            else 'bash'
        )
        LOGGER.debug("%s %s", runner, full_script_path)
        result = check_output([runner, full_script_path])
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


def test_group_of_scripts(scripts_to_test):
    """Tests all the provided scripts recursively"""
    if not scripts_to_test:
        return Promise.resolve('finished')
    script_name = scripts_to_test.pop()
    return Promise.resolve(
        test_single_script_once(script_name)
    ).then(
        lambda result: test_group_of_scripts(scripts_to_test)
    )


def test_all_the_scripts(scripts_to_test, count=0):
    """Recursively tests all scripts"""
    if 0 == count:
        return Promise.resolve('finished')
    if not scripts_to_test:
        return Promise.reject('No scripts')
    count -= 1
    return Promise.resolve(
        move_mouse_to_random_location()
    ).then(
        lambda result: Promise.resolve(
            test_group_of_scripts(scripts_to_test[:])
        )
    ).then(
        lambda result: test_all_the_scripts(scripts_to_test, count)
    )


def cli():
    """Main CLI runner"""
    bootstrap().then(
        lambda result: test_all_the_scripts(SCRIPTS_TO_TEST, RUN_COUNT)
    )

if '__main__' == __name__:
    LOGGER.info("CLI assumed")
    sys_exit(cli())
