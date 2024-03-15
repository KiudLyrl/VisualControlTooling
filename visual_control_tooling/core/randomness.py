# -*- coding: utf-8 -*

import math
import random

"""
Could be in utils.py but why not here
"""

def get_random_seconds_duration_between(small: float, big: float) -> float:

    def truncate(number, digits):
        stepper = 10.0 ** digits
        return math.trunc(stepper * number) / stepper

    return truncate(random.uniform(small, big), 2)

def shuffle_list(l: list) -> list:
    random.shuffle(l)
    return l # return is not needed but you won't get None if you use it by mistake

def get_random_int(small: int, big: int) -> int:
    return random.randrange(small, big+1, 1)
