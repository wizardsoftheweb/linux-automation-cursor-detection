# pylint: disable=misplaced-comparison-constant
"""This file runs the provided scripts many times to collect data"""
from __future__ import print_function

from csv import writer, QUOTE_NONNUMERIC
from os.path import dirname, isfile, join, splitext
from random import randrange, seed
from re import search, MULTILINE
from subprocess import check_output
from sys import exit as sys_exit, stderr
from time import sleep, time as unix_time

import logging

from promise import Promise

import pyautogui

DEFAULT_SEED = 47
RUN_COUNT = 200
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


def log_test(script_name, run_time, final_x, final_y, finished=unix_time()):
    """Log a test row"""
    # print('Opening log')
    with open(DATA_FILE_NAME, 'a') as log_file:
        # print('Logging')
        log_writer = writer(
            log_file,
            delimiter=',',
            quotechar='"',
            quoting=QUOTE_NONNUMERIC
        )
        log_writer.writerow(
            [script_name, run_time, final_x, final_y, finished]
        )
        return Promise.resolve('logged')
    # print('Logging failed')
    return Promise.reject('Unable to log')


def bootstrap():
    """Creates the initial state"""
    seed(DEFAULT_SEED)
    return Promise.resolve(
        log_test('script_name', 'run_time', 'final_x', 'final_y', 'finished')
    )


def get_random_point():
    """Returns a random coordinate on the screen"""
    return randrange(0, SCREEN_WIDTH), randrange(0, SCREEN_HEIGHT)


def move_mouse_to_random_location(delay=0):
    """Moves the mouse to a new location after a possible delay"""
    # print("Sleeping mouse movement %ds" % (delay))
    sleep(delay)
    # print('Moving mouse')
    x_coordinate, y_coordinate = get_random_point()
    pyautogui.moveTo(x_coordinate, y_coordinate)
    return Promise.resolve((x_coordinate, y_coordinate))


def parse_difference(haystack):
    """Finds the result from stdout"""
    possible_result = search(
        r'^Difference:\s+(?P<diff>[\d.]+).*?$',
        haystack,
        MULTILINE
    )
    # print(possible_result.group('diff'))
    if possible_result.group('diff'):
        # print('Returning results')
        return Promise.resolve(possible_result.group('diff'))
    # print('Difference failed')
    return Promise.reject('Difference not found')


def execute_script(script_name):
    """Runs the given script"""
    extension = splitext(script_name)
    full_script_path = join(SCRIPTS_PATH, script_name)
    if isfile(full_script_path):
        runner = (
            ['python']
            if '.py' == extension[1]
            else ['bash']
        )
        # print(full_script_path)
        result = check_output(runner + [full_script_path])
        return Promise(
            lambda resolve, reject: resolve(parse_difference(result))
        ).then(
            lambda result: Promise.resolve(
                float(result) * (1000 if extension[1] == '.py' else 1)
            )
        )
    return Promise.reject("%s failed" % (script_name))


def test_single_script_once(script_name):
    """Tests a single script"""
    return Promise.all([
        Promise.resolve(move_mouse_to_random_location()),
        Promise.resolve(execute_script(script_name)),
    ]).then(
        lambda result: Promise.resolve(
            [script_name, result[1], result[0][0], result[0][1]]
        )
    ).then(lambda result: Promise.resolve(log_test(*result)))


def fully_test_single_script(script_name, count=0):
    """Recursively tests a single script"""
    # print('Calling %s %d time(s)' % (script_name, count))
    if 0 == count:
        return Promise.resolve('finished')
    count -= 1
    return Promise.resolve(
        test_single_script_once(script_name)
    ).then(
        lambda result: fully_test_single_script(script_name, count)
    )


def test_all_the_scripts(scripts_to_test):
    """Tests all the provided scripts recursively"""
    if not scripts_to_test:
        return Promise.resolve('finished')
    script_name = scripts_to_test.pop()
    return Promise.resolve(
        fully_test_single_script(script_name, RUN_COUNT)
    ).then(
        lambda result: test_all_the_scripts(scripts_to_test)
    )


def cli():
    """Main CLI runner"""
    bootstrap().then(
        lambda result: test_all_the_scripts(SCRIPTS_TO_TEST)
    )

if '__main__' == __name__:
    sys_exit(cli())
