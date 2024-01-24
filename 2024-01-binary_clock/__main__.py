import datetime
import sys
import time

from .proper import binarify


def current_binary_timestamp() -> str:
    current_time: datetime.datetime = datetime.datetime.now()

    return binarify(current_time.strftime('%H:%M:%S'))


def time_to_next_sec() -> datetime.timedelta:
    current_time: datetime.datetime = datetime.datetime.now()

    next_sec: datetime.datetime = current_time.replace(microsecond=0) + datetime.timedelta(seconds=1)

    return next_sec - current_time


while True:
    binary_timestamp: str = current_binary_timestamp()

    print(binary_timestamp)
    print(f'\033[{len(binary_timestamp.splitlines())}A', end='') # Go back to the top

    time.sleep(time_to_next_sec().total_seconds())
